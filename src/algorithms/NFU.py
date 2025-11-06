from typing import Iterable, Set, Dict, List
from baseAlgorithm import PageReplacementAlgorithm
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult
from src.core import Access, PTE
import matplotlib.pyplot as plt

class NFU(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("NFU")

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
                last_used=None
            )
            for pid in all_pages
        }

        # Adiciona campo auxiliar para contagem de acessos
        usage_counter: Dict[int, int] = {pid: 0 for pid in all_pages}

        frames_list: List[PTE] = []
        faults = hits = evictions = 0
        time = 0

        for acc in seq:
            time += 1
            pte = page_table[acc.page_id]

            # Caso de HIT
            if pte.frame is not None:
                hits += 1
                pte.R = 1
                if acc.write:
                    pte.M = 1
                usage_counter[pte.page_id] += 1
                pte.last_used = time
                continue

            faults += 1

            if len(frames_list) < frames:
                pte.frame = len(frames_list)
                pte.R = 1
                pte.M = int(acc.write)
                pte.loaded_at = time
                pte.last_used = time
                usage_counter[pte.page_id] = 1
                frames_list.append(pte)
                continue

            victim = min(frames_list, key=lambda x: usage_counter[x.page_id])
            evictions += 1

            victim_frame = victim.frame
            frames_list.remove(victim)
            victim.frame = None

            pte.frame = victim_frame
            pte.R = 1
            pte.M = int(acc.write)
            pte.loaded_at = time
            pte.last_used = time
            usage_counter[pte.page_id] = 1
            frames_list.append(pte)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )