from collections import deque
from typing import Iterable, Set
import matplotlib.pyplot as plt

from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult
from src.access import Access

class Fifo(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("FIFO")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames must be greater than 0")

        seq = self._normalize_trace(trace)
        q = deque()
        in_mem: Set[int] = set()

        faults = hits = evictions = 0
        trace_len = 0

        for acc in seq:
            trace_len += 1
            pid = acc.page.id

            if pid in in_mem:
                hits += 1
                continue

            faults += 1
            if len(q) < frames:
                q.append(pid)
                in_mem.add(pid)
            else:
                old = q.popleft()
                in_mem.remove(old)
                evictions += 1
                q.append(pid)
                in_mem.add(pid)

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )

    def plot(self, save_path: str | None = None, show: bool = True) -> None:
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
