from abc import ABC, abstractmethod
from typing import Iterable, List, Optional
from src.core import BenchmarkResult, Access, RunResult


class PageReplacementAlgorithm(ABC):
    """
    Base para algoritmos de substituição de páginas
    Contrato:
      - run(trace, frames) -> RunResult
      - benchmark(trace, frames_list) -> BenchmarkResult
      - plot(...) -> None
    """
    def __init__(self, name: str):
        self.name = name
        self._last_benchmark: Optional[BenchmarkResult] = None

    def _normalize_trace(self, trace: Iterable[Access]) -> List[Access]:
        seq = list(trace)
        if not all(isinstance(a, Access) for a in seq):
            raise TypeError("O traço deve conter apenas objetos Access.")
        return seq

    @abstractmethod
    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        ...

    def benchmark(self, trace: Iterable[Access], frames_list: Iterable[int]) -> BenchmarkResult:
        print(f"--- Benchmark {self.name} ---")
        seq = self._normalize_trace(trace)
        results = [self.run(seq, frames) for frames in frames_list]
        br = BenchmarkResult(algo_name=self.name, results=results)
        self._last_benchmark = br
        for result in br.results:
            print(
                f"Frames = {result.frames:2d} | Faults = {result.faults:2d} | Hits = {result.hits:2d} "
                f"| HitRate = {result.hit_rate:.2f} | FaultRate = {result.fault_rate:.2f}"
            )
        return br

    @abstractmethod
    def plot(self, *args, **kwargs) -> None:
        ...

    @property
    def last_benchmark(self) -> Optional[BenchmarkResult]:
        return self._last_benchmark
