from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional
from src.access import Access

@dataclass(frozen=True)
class RunResult:
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
    algo_name: str
    results: List[RunResult]


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
        for r in br.results:
            print(
                f"Frames = {r.frames:2d} | Faults = {r.faults:2d} | Hits = {r.hits:2d} "
                f"| HitRate = {r.hit_rate:.2f} | FaultRate = {r.fault_rate:.2f}"
            )
        return br

    @abstractmethod
    def plot(self, *args, **kwargs) -> None:
        ...

    @property
    def last_benchmark(self) -> Optional[BenchmarkResult]:
        return self._last_benchmark
