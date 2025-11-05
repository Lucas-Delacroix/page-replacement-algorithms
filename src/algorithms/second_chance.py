from typing import Dict, Iterable, List, Optional
import matplotlib.pyplot as plt
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, RunResult, PTE


class SecondChance(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("SecondChance")
        self.pointer: int = 0

    def _advance(self, n: int) -> None:
        """Avança o ponteiro do relógio (mod n)."""
        if n > 0:
            self.pointer = (self.pointer + 1) % n

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        faults = hits = evictions = 0
        seq: List[Access] = list(trace)
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        page_table: Dict[int, PTE] = {}
        clock: List[int] = []
        self.pointer = 0

        free_frames = list(range(frames))
        t_default = 0

        for page in seq:
            pid = page.page_id
            t = page.t if page.t is not None else t_default
            t_default += 1

            if pid in page_table:
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if page.write:
                    pte.M = 1
                pte.last_used = t
                continue

            faults += 1

            if free_frames:
                f = free_frames.pop(0)
                pte = PTE(page_id=pid, frame=f, R=1, M=1 if page.write else 0,
                          loaded_at=t, last_used=t)
                page_table[pid] = pte
                clock.append(pid)
            else:
                n = len(clock)
                while True:
                    victim_pid = clock[self.pointer]
                    victim_pte = page_table[victim_pid]
                    if victim_pte.R == 1:
                        victim_pte.R = 0
                        self._advance(n)
                    else:
                        evictions += 1
                        f = victim_pte.frame
                        clock[self.pointer] = pid
                        del page_table[victim_pid]
                        page_table[pid] = PTE(page_id=pid, frame=f, R=1,
                                              M=1 if page.write else 0,
                                              loaded_at=t, last_used=t)
                        self._advance(n)
                        break

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=len(seq),
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
