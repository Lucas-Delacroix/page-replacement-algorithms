from __future__ import annotations
import matplotlib.pyplot as plt
from collections import deque
from typing import Dict, Iterable, List
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, RunResult, PTE


class Fifo(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("FIFO")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        seq: List[Access] = list(trace)
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        page_table: Dict[int, PTE] = {}
        free_frames = deque(range(frames))
        fifo_queue = deque()

        faults = hits = evictions = 0

        for a in seq:
            pid = a.page_id

            if pid in page_table:
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if a.write:
                    pte.M = 1
            else:
                faults += 1

                if free_frames:
                    f = free_frames.popleft()
                else:
                    victim_pid = fifo_queue.popleft()
                    victim = page_table.pop(victim_pid)
                    evictions += 1
                    f = victim.frame

                pte = PTE(page_id=pid, frame=f, R=1, M=1 if a.write else 0, loaded_at=a.t, last_used=a.t)
                page_table[pid] = pte
                fifo_queue.append(pid)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=len(seq),
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
