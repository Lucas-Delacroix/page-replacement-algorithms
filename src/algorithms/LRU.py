from typing import Dict, Iterable, List, Optional, Set

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, RunResult, PTE

class LRU(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("LRU")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        trace_len = len(seq)

        self._trace_begin(frames)

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

        faults = hits = evictions = 0
        time: int = 0
        fallback_t = 0

        def build_frames_state() -> List[dict]:
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pte in page_table.values():
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
                            "meta": {"last_used": None},
                        }
                    )
                else:
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": slot.page_id,
                            "R": slot.R,
                            "M": slot.M,
                            "meta": {"last_used": slot.last_used},
                        }
                    )
            return state

        for acc in seq:
            if acc.t is not None:
                current_t = acc.t
            else:
                current_t = fallback_t
                fallback_t += 1

            pte: PTE = page_table[acc.page_id]
            evicted_pid: Optional[int] = None
            victim_pid_meta: Optional[int] = None

            if pte.frame is not None:
                hit = True
                hits += 1
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = time
            else:
                hit = False
                faults += 1

                if len(frames_list) < frames:
                    pte.frame = len(frames_list)
                    pte.R = 1
                    pte.M = int(acc.write)
                    pte.loaded_at = time
                    pte.last_used = time
                    frames_list.append(pte)
                else:
                    victim = min(frames_list, key=lambda x: x.last_used)
                    victim_pid_meta = victim.page_id
                    evictions += 1

                    victim_frame = victim.frame
                    frames_list.remove(victim)
                    victim.frame = None

                    pte.frame = victim_frame
                    pte.R = 1
                    pte.M = int(acc.write)
                    pte.loaded_at = time
                    pte.last_used = time
                    frames_list.append(pte)
                    evicted_pid = victim_pid_meta

            self.trace_step(
                t=current_t,
                access_page=acc.page_id,
                access_write=acc.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "lru",
                    "frames_used": len(frames_list),
                    "victim": victim_pid_meta,
                },
            )

            time += 1

        self._trace_end(frames)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
