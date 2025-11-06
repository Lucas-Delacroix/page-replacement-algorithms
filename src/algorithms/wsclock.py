from __future__ import annotations

from typing import Dict, Iterable, List

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

        page_table: Dict[int, PTE] = {}
        clock: List[int] = []
        free_frames = list(range(frames))
        self.pointer = 0

        time_fallback = 0

        for acc in seq:
            pid = acc.page_id
            t = acc.t if acc.t is not None else time_fallback
            time_fallback += 1

            if pid in page_table:
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = t
                continue

            faults += 1

            if free_frames:
                frame = free_frames.pop(0)
                pte = PTE(page_id=pid, frame=frame, R=1, M=int(acc.write), loaded_at=t, last_used=t)
                page_table[pid] = pte
                clock.append(pid)
                continue

            victim_index = self._find_victim(page_table, clock, current_time=t)
            victim_pid = clock[victim_index]
            victim_pte = page_table.pop(victim_pid)
            evictions += 1

            frame = victim_pte.frame
            clock[victim_index] = pid

            pte = PTE(page_id=pid, frame=frame, R=1, M=int(acc.write), loaded_at=t, last_used=t)
            page_table[pid] = pte

            self.pointer = (victim_index + 1) % len(clock)

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
