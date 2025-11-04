from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional

@dataclass(frozen=True)
class RunResult:
    """Resultado de UMA execução do algoritmo para um dado 'frames'."""
    algo_name: str
    frames: int
    trace_len: int
    faults: int
    hits: int
    evictions: int

    @property
    def hit_rate(self) -> float:
        return self.hits / self.trace_len if self.trace_len else 0.0

    @property
    def fault_rate(self) -> float:
        return self.faults / self.trace_len if self.trace_len else 0.0


@dataclass
class BenchmarkResult:
    """Coleção ordenada de RunResult (um por valor de frames)."""
    algo_name: str
    results: List[RunResult]

class PageReplacementAlgorithm(ABC):
    """
    Base para algoritmos de substituição de páginas.
    Contrato:
      - run(trace, frames) -> RunResult
      - benchmark(trace, frames_list) -> BenchmarkResult (e atualiza _last_benchmark)
      - plot() -> None (plota a partir do último benchmark)
    """

    def __init__(self, name: str):
        self.name = name
        self._last_benchmark: Optional[BenchmarkResult] = None


    def _normalize_trace(self, trace: Iterable[int]) -> List[int]:
        """Converte o traço para lista para evitar consumo múltiplo de iteráveis."""
        return list(trace)


    @abstractmethod
    def run(self, trace: Iterable[int], frames: int) -> RunResult:
        """Executa o algoritmo em um traço e retorna métricas padronizadas."""
        ...

    def benchmark(self, trace: Iterable[int], frames_list: Iterable[int]) -> BenchmarkResult:
        """
        Executa 'run' para cada frames em 'frames_list' (mesma ordem),
        retorna BenchmarkResult e atualiza self._last_benchmark.
        """
        print(f"--- Benchmark {self.name} ---")
        seq = self._normalize_trace(trace)
        results = [self.run(seq, frames) for frames in frames_list]
        benchmark_result = BenchmarkResult(algo_name=self.name, results=results)
        self._last_benchmark = benchmark_result
        for r in benchmark_result.results:
            print(
                f"Frames = {r.frames:2d} | Faults = {r.faults:2d} | Hits = {r.hits:2d} "
                f"| HitRate = {r.hit_rate:.2f} | FaultRate = {r.fault_rate:.2f}"
            )
        return benchmark_result

    @abstractmethod
    def plot(self) -> None:
        """Plota um gráfico usando self._last_benchmark."""
        ...

    @property
    def last_benchmark(self) -> Optional[BenchmarkResult]:
        return self._last_benchmark
