from typing import Dict, Iterable, List, Optional

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

        self._trace_begin(frames)

        page_table: Dict[int, PTE] = {}
        clock: List[int] = []
        self.pointer = 0

        free_frames = list(range(frames))
        t_default = 0

        def build_frames_state() -> List[dict]:
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pte in page_table.values():
                if pte.frame is not None and 0 <= pte.frame < frames:
                    frames_pte[pte.frame] = pte

            clock_indexes = {pid: idx for idx, pid in enumerate(clock)}
            hand_pos = self.pointer % len(clock) if clock else None

            state: List[dict] = []
            for i, slot in enumerate(frames_pte):
                if slot is None:
                    state.append(
                        {
                            "frame_index": i,
                            "page_id": None,
                            "R": 0,
                            "M": 0,
                            "meta": {"hand": hand_pos},
                        }
                    )
                else:
                    state.append(
                        {
                            "frame_index": i,
                            "page_id": slot.page_id,
                            "R": slot.R,
                            "M": slot.M,
                            "meta": {
                                "hand": hand_pos,
                                "clock_slot": clock_indexes.get(slot.page_id),
                            },
                        }
                    )
            return state

        for page in seq:
            pid = page.page_id
            current_t = page.t if page.t is not None else t_default
            if page.t is None:
                t_default += 1

            evicted_pid: Optional[int] = None

            if pid in page_table:
                hit = True
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                if page.write:
                    pte.M = 1
                pte.last_used = current_t
            else:
                hit = False
                faults += 1

                if free_frames:
                    f = free_frames.pop(0)
                    page_table[pid] = PTE(
                        page_id=pid,
                        frame=f,
                        R=1,
                        M=1 if page.write else 0,
                        loaded_at=current_t,
                        last_used=current_t,
                    )
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
                            evicted_pid = victim_pid
                            f = victim_pte.frame
                            clock[self.pointer] = pid
                            del page_table[victim_pid]
                            page_table[pid] = PTE(
                                page_id=pid,
                                frame=f,
                                R=1,
                                M=1 if page.write else 0,
                                loaded_at=current_t,
                                last_used=current_t,
                            )
                            self._advance(n)
                            break

            self.trace_step(
                t=current_t,
                access_page=pid,
                access_write=page.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "second_chance",
                    "pointer": self.pointer % len(clock) if clock else None,
                    "clock_size": len(clock),
                    "free_frames": len(free_frames),
                },
            )

        self._trace_end(frames)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=len(seq),
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
