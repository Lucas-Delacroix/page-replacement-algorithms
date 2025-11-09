from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Dict, Any
import os
import matplotlib.pyplot as plt
from src.core import BenchmarkResult, Access, RunResult
from src.trace import RunTrace, StepLog, FrameSnapshot


class PageReplacementAlgorithm(ABC):
    """
    Base para algoritmos de substituição de páginas.

    Responsabilidades:
      - normalizar o traço
      - rodar benchmark (chamar run() para cada frames)
      - armazenar o último BenchmarkResult
      - armazenar RunTrace por frames (quando trace_enabled=True)
    """

    def __init__(self, name: str):
        self.name = name
        self._last_benchmark: Optional[BenchmarkResult] = None
        self._trace_enabled: bool = False
        self._trace_current: Optional[RunTrace] = None
        self._last_trace_by_frames: dict[int, RunTrace] = {}


    def _trace_begin(self, frames: int) -> None:
        """Inicia o registro de um run(trace, frames)."""
        if self._trace_enabled:
            self._trace_current = RunTrace(algo_name=self.name, frames=frames)

    def trace_step(
        self,
        *,
        t: int,
        access_page: int,
        access_write: bool,
        hit: bool,
        evicted_page: Optional[int],
        frames_state: List[Dict[str, Any]],
        decision_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Registra UM passo da execução.

        frames_state: lista de dicts com:
          - frame_index (int)
          - page_id (int | None)
          - R (int)
          - M (int)
          - meta (dict opcional)
        """
        if not self._trace_enabled or self._trace_current is None:
            return

        snapshots = [
            FrameSnapshot(
                frame_index=int(fs["frame_index"]),
                page_id=fs.get("page_id"),
                R=int(fs.get("R", 0)),
                M=int(fs.get("M", 0)),
                meta=dict(fs.get("meta", {})),
            )
            for fs in frames_state
        ]

        step = StepLog(
            t=t,
            access_page=access_page,
            access_write=access_write,
            hit=hit,
            evicted_page=evicted_page,
            decision_meta=decision_meta or {},
            frames_after=snapshots,
        )
        self._trace_current.steps.append(step)

    def _trace_end(self, frames: int) -> None:
        """Finaliza o run atual e guarda o RunTrace associado a 'frames'."""
        if self._trace_enabled and self._trace_current is not None:
            self._last_trace_by_frames[frames] = self._trace_current
        self._trace_current = None

    @property
    def last_traces(self) -> dict[int, RunTrace]:
        """RunTrace para cada valor de 'frames' da última chamada a benchmark()."""
        return self._last_trace_by_frames


    def _normalize_trace(self, trace: Iterable[Access]) -> List[Access]:
        seq = list(trace)
        if not all(isinstance(a, Access) for a in seq):
            raise TypeError("O traço deve conter apenas objetos Access.")
        return seq

    @abstractmethod
    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        """
        Deve:
          - chamar self._trace_begin(frames) no início
          - chamar self.trace_step(...) a cada acesso (opcional)
          - chamar self._trace_end(frames) no fim
        """
        ...

    def benchmark(
        self,
        trace: Iterable[Access],
        frames_list: Iterable[int],
        *,
        trace_enabled: bool = True,
    ) -> BenchmarkResult:
        """
        Executa o algoritmo para cada valor em frames_list.

        Se trace_enabled=True, cada execução (run) registra um RunTrace
        acessível depois em self.last_traces.
        """
        print(f"--- Benchmark {self.name} ---")
        seq = self._normalize_trace(trace)

        self._trace_enabled = bool(trace_enabled)
        self._last_trace_by_frames.clear()

        results: List[RunResult] = []
        for frames in frames_list:
            r = self.run(seq, frames)
            results.append(r)

        br = BenchmarkResult(algo_name=self.name, results=results)
        self._last_benchmark = br

        for r in br.results:
            print(
                f"Frames={r.frames:2d} | Faults={r.faults:3d} | Hits={r.hits:3d} "
                f"| HitRate={r.hit_rate:.3f} | FaultRate={r.fault_rate:.3f}"
            )

        return br

    def plot(self, save_path: str | None = None, show: bool = False) -> None:
        os.makedirs("results/single", exist_ok=True)
        save_path = f"results/single/{save_path}" if save_path else None

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