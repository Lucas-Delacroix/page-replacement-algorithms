from typing import Iterable, List, Optional
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult

class Optimal(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("Ótimo")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        seq = self._normalize_trace(trace)
        frame_list: List[Optional[int]] = []
        hits = faults = evictions = 0

        ids = [a.page_id for a in seq]

        for i, access in enumerate(seq):
            pid = access.page_id

            if pid in frame_list:
                hits += 1
                continue

            faults += 1
            if len(frame_list) < frames:
                frame_list.append(pid)
                continue

            future = ids[i + 1 :]
            distances: List[float] = []
            for p in frame_list:
                try:
                    idx = future.index(p)
                except ValueError:
                    idx = float("inf")
                distances.append(idx)

            victim_idx = distances.index(max(distances))
            frame_list[victim_idx] = pid
            evictions += 1

        total = len(seq)
        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=total,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )