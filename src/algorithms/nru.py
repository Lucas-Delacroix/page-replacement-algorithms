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

        page_table: Dict[int, PTE] = {}
        loaded_order: List[int] = []
        free_frames = list(range(frames))

        accesses_since_reset = 0
        time_fallback = 0

        for acc in seq:
            pid = acc.page_id
            t = acc.t if acc.t is not None else time_fallback
            time_fallback += 1

            if self._should_reset(accesses_since_reset, frames):
                for loaded_pid in loaded_order:
                    page_table[loaded_pid].R = 0
                accesses_since_reset = 0

            accesses_since_reset += 1

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
                loaded_order.append(pid)
                continue

            victim_pid = self._select_victim(page_table, loaded_order)
            victim_pte = page_table.pop(victim_pid)
            loaded_order.remove(victim_pid)

            evictions += 1
            frame = victim_pte.frame

            pte = PTE(page_id=pid, frame=frame, R=1, M=int(acc.write), loaded_at=t, last_used=t)
            page_table[pid] = pte
            loaded_order.append(pid)

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
