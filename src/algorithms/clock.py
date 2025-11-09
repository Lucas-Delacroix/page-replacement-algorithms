from typing import Dict, Iterable, List, Optional, Set

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult

class Clock(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("Clock")

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
        pointer: int = 0

        faults = hits = evictions = 0
        time = 0
        fallback_t = 0

        def build_frames_state() -> List[dict]:
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pte in page_table.values():
                if pte.frame is not None and 0 <= pte.frame < frames:
                    frames_pte[pte.frame] = pte

            hand_pos = pointer % len(frames_list) if frames_list else None
            state: List[dict] = []
            for idx, slot in enumerate(frames_pte):
                if slot is None:
                    meta = {"hand": hand_pos}
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": None,
                            "R": 0,
                            "M": 0,
                            "meta": meta,
                        }
                    )
                else:
                    meta = {
                        "hand": hand_pos,
                        "hand_here": int(hand_pos == slot.frame) if hand_pos is not None else 0,
                    }
                    state.append(
                        {
                            "frame_index": idx,
                            "page_id": slot.page_id,
                            "R": slot.R,
                            "M": slot.M,
                            "meta": meta,
                        }
                    )
            return state

        for acc in seq:
            current_t: int
            if acc.t is not None:
                current_t = acc.t
            else:
                current_t = fallback_t
                fallback_t += 1

            pte: PTE = page_table[acc.page_id]
            evicted_pid: Optional[int] = None

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
                    while True:
                        current = frames_list[pointer]

                        if current.R == 0:
                            evictions += 1
                            evicted_pid = current.page_id

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
                        time += 1
                    time += 1

            self.trace_step(
                t=current_t,
                access_page=acc.page_id,
                access_write=acc.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "clock",
                    "pointer": pointer % len(frames_list) if frames_list else None,
                    "frames_loaded": len(frames_list),
                },
            )

        self._trace_end(frames)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
