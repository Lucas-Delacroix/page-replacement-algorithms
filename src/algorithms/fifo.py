from collections import deque
from typing import Iterable, List
import matplotlib.pyplot as plt
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult, BenchmarkResult


class Fifo(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("FIFO")

    def run(self, trace: Iterable[int], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames must be greater than 0")
        q = deque()
        in_mem = set()
        faults = hits = evictions = 0
        trace_len = 0

        for page in trace:
            trace_len += 1

            if page in in_mem:
                hits += 1
                continue

            faults += 1

            if len(q) < frames:
                q.append(page)
                in_mem.add(page)

            else:
                old = q.popleft()
                in_mem.add(old)
                evictions += 1
                q.append(page)
                in_mem.add(page)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )

    def plot(self, save_path: str | None = True, show: bool = False) -> None:
        """
        Plot simples: Faltas de página × Frames usando o último benchmark.
        Use suas funções externas para comparar múltiplos algoritmos.
        """
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

