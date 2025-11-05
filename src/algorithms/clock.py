from typing import Iterable, Set, Dict, List
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult
import matplotlib.pyplot as plt

class Clock(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("clock")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        trace_len = len(seq)

        all_pages = {acc.page_id for acc in seq}
        page_table: Dict[int, PTE] = {
            pid: PTE(
                page_id=pid,
                frame=None,
                R=0,
                M=0,
                loaded_at=None,
                last_used=None,
            )
            for pid in all_pages
        }


        frames_list: List[PTE] = []
        pointer: int = 0

        faults = hits = evictions = 0

        time = 0

        for acc in seq:
            pte: PTE = page_table[acc.page_id]

            if pte.frame is not None:
                hits += 1
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = time
                continue

            faults += 1

            if len(frames_list) < frames:
                pte.frame = len(frames_list)
                pte.R = 1
                pte.M = int(acc.write)
                pte.loaded_at = time
                pte.last_used = time

                frames_list.append(pte)
                continue

            while True:
                current = frames_list[pointer]

                if current.R == 0:
                    evictions += 1

                    current.frame = None
                    current.R = 0
                    current.M = 0

                    pte.frame = pointer
                    pte.R = 1
                    pte.M = int(acc.write)
                    pte.loaded_at = time
                    pte.last_used = time

                    frames_list[pointer] = pte

                    pointer = (pointer + 1) % frames
                    break
                else:
                    current.R = 0
                    pointer = (pointer + 1) % frames

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )