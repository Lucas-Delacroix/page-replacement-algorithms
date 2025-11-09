from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult


class NRU(PageReplacementAlgorithm):
    def __init__(self, reset_interval: Optional[int] = None):
        super().__init__("NRU")
        self.reset_interval = reset_interval

    def _should_reset(self, accesses_since_reset: int, frames: int) -> bool:
        interval = self.reset_interval or max(1, frames * 2)
        return accesses_since_reset >= interval

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        faults = hits = evictions = 0

        self._trace_begin(frames)

        page_table: Dict[int, PTE] = {}
        loaded_order: List[int] = []
        free_frames = list(range(frames))

        accesses_since_reset = 0
        time_fallback = 0

        def build_frames_state() -> List[dict]:
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pid, pte in page_table.items():
                if pte.frame is not None and 0 <= pte.frame < frames:
                    frames_pte[pte.frame] = pte

            state: List[dict] = []
            for idx, slot in enumerate(frames_pte):
                if slot is None:
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": None,
                            "R": 0,
                            "M": 0,
                            "meta": {"class": None},
                        }
                    )
                else:
                    nru_class = (slot.R << 1) | slot.M
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": slot.page_id,
                            "R": slot.R,
                            "M": slot.M,
                            "meta": {"class": nru_class},
                        }
                    )
            return state

        for acc in seq:
            pid = acc.page_id
            current_t = acc.t if acc.t is not None else time_fallback
            time_fallback += 1

            reset_applied = False
            if self._should_reset(accesses_since_reset, frames):
                for loaded_pid in loaded_order:
                    page_table[loaded_pid].R = 0
                accesses_since_reset = 0
                reset_applied = True

            accesses_since_reset += 1

            evicted_pid: Optional[int] = None

            if pid in page_table:
                hit = True
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = current_t
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
                        loaded_at=current_t,
                        last_used=current_t,
                    )
                    page_table[pid] = pte
                    loaded_order.append(pid)
                else:
                    victim_pid = self._select_victim(page_table, loaded_order)
                    victim_pte = page_table.pop(victim_pid)
                    loaded_order.remove(victim_pid)

                    evictions += 1
                    evicted_pid = victim_pid
                    frame = victim_pte.frame

                    pte = PTE(
                        page_id=pid,
                        frame=frame,
                        R=1,
                        M=int(acc.write),
                        loaded_at=current_t,
                        last_used=current_t,
                    )
                    page_table[pid] = pte
                    loaded_order.append(pid)

            self.trace_step(
                t=current_t,
                access_page=pid,
                access_write=acc.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "nru",
                    "reset": reset_applied,
                    "accesses_since_reset": accesses_since_reset,
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

    def _select_victim(self, page_table: Dict[int, PTE], loaded_order: List[int]) -> int:
        classes: Dict[int, List[int]] = {0: [], 1: [], 2: [], 3: []}
        for pid in loaded_order:
            pte = page_table[pid]
            cls = (pte.R << 1) | pte.M
            classes[cls].append(pid)

        for cls in range(4):
            if classes[cls]:
                return classes[cls][0]

        raise RuntimeError("Nenhuma página disponível para substituição.")
