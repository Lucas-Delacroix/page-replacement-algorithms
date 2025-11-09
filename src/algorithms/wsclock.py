from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult


class WSClock(PageReplacementAlgorithm):
    def __init__(self, window: int = 4):
        if window < 0:
            raise ValueError("window deve ser >= 0")
        super().__init__("WSClock")
        self.window = window
        self.pointer = 0

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        faults = hits = evictions = 0

        self._trace_begin(frames)

        page_table: Dict[int, PTE] = {}
        clock: List[int] = []
        free_frames = list(range(frames))
        self.pointer = 0

        time_fallback = 0

        def build_frames_state() -> List[dict]:
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pid, pte in page_table.items():
                if pte.frame is not None and 0 <= pte.frame < frames:
                    frames_pte[pte.frame] = pte

            clock_pos = {pid: idx for idx, pid in enumerate(clock)}
            hand_pos = self.pointer % len(clock) if clock else None

            state: List[dict] = []
            for idx, slot in enumerate(frames_pte):
                if slot is None:
                    meta = {"hand": hand_pos, "window": self.window}
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": None,
                            "R": 0,
                            "M": 0,
                            "meta": meta,
                        }
                    )
                else:
                    meta = {
                        "hand": hand_pos,
                        "clock_slot": clock_pos.get(slot.page_id),
                        "window": self.window,
                        "age": (time_fallback - slot.last_used) if slot.last_used is not None else None,
                    }
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": slot.page_id,
                            "R": slot.R,
                            "M": slot.M,
                            "meta": meta,
                        }
                    )
            return state

        for acc in seq:
            pid = acc.page_id
            t = acc.t if acc.t is not None else time_fallback
            time_fallback += 1

            evicted_pid: Optional[int] = None
            victim_index_meta: Optional[int] = None

            if pid in page_table:
                hit = True
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = t
            else:
                hit = False
                faults += 1

                if free_frames:
                    frame = free_frames.pop(0)
                    pte = PTE(
                        page_id=pid,
                        frame=frame,
                        R=1,
                        M=int(acc.write),
                        loaded_at=t,
                        last_used=t,
                    )
                    page_table[pid] = pte
                    clock.append(pid)
                else:
                    victim_index = self._find_victim(page_table, clock, current_time=t)
                    victim_index_meta = victim_index
                    victim_pid = clock[victim_index]
                    victim_pte = page_table.pop(victim_pid)
                    evictions += 1

                    frame = victim_pte.frame
                    clock[victim_index] = pid

                    pte = PTE(
                        page_id=pid,
                        frame=frame,
                        R=1,
                        M=int(acc.write),
                        loaded_at=t,
                        last_used=t,
                    )
                    page_table[pid] = pte

                    self.pointer = (victim_index + 1) % len(clock)
                    evicted_pid = victim_pid

            self.trace_step(
                t=t,
                access_page=pid,
                access_write=acc.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "wsclock",
                    "pointer": self.pointer % len(clock) if clock else None,
                    "window": self.window,
                    "victim_index": victim_index_meta,
                },
            )

        self._trace_end(frames)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=len(seq),
            faults=faults,
            hits=hits,
            evictions=evictions,
        )

    def _find_victim(self, page_table: Dict[int, PTE], clock: List[int], current_time: int) -> int:
        n = len(clock)
        if n == 0:
            raise RuntimeError("Relógio vazio durante a substituição.")

        start = self.pointer % n
        index = start
        visited_full_cycle = False

        while True:
            pid = clock[index]
            pte = page_table[pid]

            age = float("inf")
            if pte.last_used is not None and current_time is not None:
                age = current_time - pte.last_used

            if pte.R == 1:
                pte.R = 0
            else:
                should_replace = False
                if age > self.window:
                    if pte.M == 0:
                        should_replace = True
                    elif visited_full_cycle:
                        should_replace = True
                    else:
                        pte.M = 0
                elif visited_full_cycle:
                    should_replace = True

                if should_replace:
                    return index

            index = (index + 1) % n
            if index == start:
                if visited_full_cycle:
                    return index
                visited_full_cycle = True
