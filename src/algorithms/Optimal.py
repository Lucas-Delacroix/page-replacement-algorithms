from typing import Dict, Iterable, List, Optional

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult


class Optimal(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("Otimo")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        seq = self._normalize_trace(trace)
        frame_list: List[Optional[int]] = []
        hits = faults = evictions = 0

        self._trace_begin(frames)

        page_table: Dict[int, PTE] = {}
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

        ids = [a.page_id for a in seq]

        for i, access in enumerate(seq):
            if access.t is not None:
                current_t = access.t
            else:
                current_t = fallback_t
                fallback_t += 1

            pid = access.page_id
            evicted_pid: Optional[int] = None
            victim_idx_meta: Optional[int] = None

            if pid in page_table and page_table[pid].frame is not None:
                hit = True
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if access.write:
                    pte.M = 1
                pte.last_used = current_t
            else:
                hit = False
                faults += 1

                if len(frame_list) < frames:
                    frame_idx = len(frame_list)
                    frame_list.append(pid)
                else:
                    future = ids[i + 1 :]
                    distances: List[float] = []
                    for p in frame_list:
                        try:
                            idx = future.index(p)
                        except ValueError:
                            idx = float("inf")
                        distances.append(idx)

                    victim_idx = distances.index(max(distances))
                    victim_idx_meta = victim_idx
                    victim_pid = frame_list[victim_idx]
                    evicted_pid = victim_pid
                    evictions += 1

                    if victim_pid is not None and victim_pid in page_table:
                        del page_table[victim_pid]

                    frame_list[victim_idx] = pid
                    frame_idx = victim_idx

                page_table[pid] = PTE(
                    page_id=pid,
                    frame=frame_idx,
                    R=1,
                    M=1 if access.write else 0,
                    loaded_at=current_t,
                    last_used=current_t,
                )

            self.trace_step(
                t=current_t,
                access_page=pid,
                access_write=access.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "optimal",
                    "victim_index": victim_idx_meta,
                    "frames_used": len(frame_list),
                },
            )

        self._trace_end(frames)

        total = len(seq)
        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=total,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
