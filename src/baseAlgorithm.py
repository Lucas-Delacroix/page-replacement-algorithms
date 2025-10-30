from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List


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
    """
    Conjunto ordenado de resultados (um por valor de 'frames').
    A ordem dos itens em 'results' deve corresponder à ordem de 'frames_list' usada.
    """
    algo_name: str
    results: List[RunResult]



class PageReplacementAlgorithm(ABC):
    """
        Classe base para algoritmos de substituição de páginas.
        Define a interface que todos os algoritmos devem implementar.
    """

    def __init__(self, name: str):
        self.name = name
        self._last_benchmark: BenchmarkResult | None = None


    @abstractmethod
    def run(self, trace: Iterable[int], frames: int) -> RunResult:
        """
        Executa o algoritmo em um traço de referências.
        Deve retornar métricas como número de faltas, acertos, etc.
        """
        pass

    @abstractmethod
    def benchmark(self, trace: Iterable[int], frames_list: Iterable[int]) -> BenchmarkResult:
        """
        Executa 'run' para cada valor de 'frames' em 'frames_list' (na mesma ordem)
        e retorna um BenchmarkResult com a coleção de RunResult.
        Também deve atualizar 'self._last_benchmark'.
        """
        pass

    @abstractmethod
    def plot(self) -> None:
        """
        Plota um gráfico usando 'self._last_benchmark'.
        Implementações podem escolher a métrica (ex.: faults vs frames)
        ou aceitar um parâmetro adicional em subclasses se necessário.
        """
        ...