from __future__ import annotations

from typing import Dict, Iterable, List

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult


class WorkingSet(PageReplacementAlgorithm):
    def __init__(self, window: int = 4):
        if window <= 0:
            raise ValueError("window deve ser > 0")
        super().__init__("WorkingSet")
        self.window = window

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        faults = hits = evictions = 0

        page_table: Dict[int, PTE] = {}
        loaded_pages: List[int] = []
        free_frames = list(range(frames))

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
                loaded_pages.append(pid)
                continue

            victim_pid = self._select_victim(page_table, loaded_pages, current_time=t)
            victim_pte = page_table.pop(victim_pid)
            loaded_pages.remove(victim_pid)
            evictions += 1

            frame = victim_pte.frame
            pte = PTE(page_id=pid, frame=frame, R=1, M=int(acc.write), loaded_at=t, last_used=t)
            page_table[pid] = pte
            loaded_pages.append(pid)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=len(seq),
            faults=faults,
            hits=hits,
            evictions=evictions,
        )

    def _select_victim(self, page_table: Dict[int, PTE], loaded_pages: List[int], current_time: int) -> int:
        window_start = current_time - self.window
        candidate_pid = None
        candidate_time = None
        lru_pid = None
        lru_time = None

        for pid in loaded_pages:
            pte = page_table[pid]
            last_used = pte.last_used if pte.last_used is not None else -float("inf")

            if lru_time is None or last_used < lru_time:
                lru_pid = pid
                lru_time = last_used

            if last_used <= window_start:
                if candidate_time is None or last_used < candidate_time:
                    candidate_pid = pid
                    candidate_time = last_used

        if candidate_pid is not None:
            return candidate_pid
        if lru_pid is not None:
            return lru_pid
        raise RuntimeError("Nenhuma página disponível para substituição.")
