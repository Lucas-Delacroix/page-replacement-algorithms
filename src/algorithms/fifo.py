from collections import deque
from typing import Dict, Iterable, List, Optional
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, RunResult, PTE


class Fifo(PageReplacementAlgorithm):
    def __init__(self) -> None:
        super().__init__("FIFO")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        """
        Implementação do FIFO com rastreamento opcional.

        Estruturas:
          - page_table: mapeia pid -> PTE
          - free_frames: fila de frames livres
          - fifo_queue: fila FIFO de pids (ordem de chegada)
        """
        seq: List[Access] = list(trace)
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        self._trace_begin(frames)

        page_table: Dict[int, PTE] = {}
        free_frames = deque(range(frames))
        fifo_queue = deque()

        faults = 0
        hits = 0
        evictions = 0

        def build_frames_state() -> List[dict]:
            """
            Constrói o estado atual dos frames para fins de log.
            """
            frames_pte: List[Optional[PTE]] = [None] * frames
            for pte in page_table.values():
                if 0 <= pte.frame < frames:
                    frames_pte[pte.frame] = pte

            state: List[dict] = []
            for i in range(frames):
                pte = frames_pte[i]
                if pte is None:
                    state.append(
                        {
                            "frame_index": i,
                            "page_id": None,
                            "R": 0,
                            "M": 0,
                            "meta": {},
                        }
                    )
                else:
                    state.append(
                        {
                            "frame_index": i,
                            "page_id": pte.page_id,
                            "R": pte.R,
                            "M": pte.M,
                            "meta": {
                                "loaded_at": pte.loaded_at,
                                "last_used": pte.last_used,
                            },
                        }
                    )
            return state

        for t_idx, a in enumerate(seq):
            pid = a.page_id
            current_t = a.t if a.t is not None else t_idx

            evicted_pid: Optional[int] = None

            if pid in page_table:
                hit = True
                hits += 1
                pte = page_table[pid]
                pte.R = 1
                pte.last_used = current_t
                if a.write:
                    pte.M = 1
            else:
                hit = False
                faults += 1

                if free_frames:
                    f = free_frames.popleft()
                else:
                    victim_pid = fifo_queue.popleft()
                    victim = page_table.pop(victim_pid)
                    evictions += 1
                    evicted_pid = victim_pid
                    f = victim.frame

                pte = PTE(
                    page_id=pid,
                    frame=f,
                    R=1,
                    M=1 if a.write else 0,
                    loaded_at=current_t,
                    last_used=current_t,
                )
                page_table[pid] = pte
                fifo_queue.append(pid)

            self.trace_step(
                t=current_t,
                access_page=pid,
                access_write=a.write,
                hit=hit,
                evicted_page=evicted_pid,
                frames_state=build_frames_state(),
                decision_meta={
                    "policy": "fifo",
                    "queue_len": len(fifo_queue),
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