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

    def plot(self, save_path: str | None = None, show: bool = False) -> None:
        if self._last_benchmark is None:
            raise RuntimeError("Sem benchmark: chame benchmark() antes de plot().")

        frames = [r.frames for r in self._last_benchmark.results]
        faults = [r.faults for r in self._last_benchmark.results]

        plt.figure()
        plt.plot(frames, faults, marker="o", label=self._last_benchmark.algo_name)
        plt.xlabel("Frames")
        plt.ylabel("Faltas de página")
        plt.title(f"{self.name} — Faltas de página")
        plt.grid(True, linestyle="--", linewidth=0.5)
        plt.legend()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Gráfico salvo em: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()