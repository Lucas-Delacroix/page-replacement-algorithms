from abc import ABC, abstractmethod
from typing import Iterable

class PageReplacementAlgorithm(ABC):
    """
        Classe base para algoritmos de substituição de páginas.
        Define a interface que todos os algoritmos devem implementar.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, trace: Iterable[int], frames: int) -> dict:
        """
        Executa o algoritmo em um traço de referências.
        Deve retornar métricas como número de faltas, acertos, etc.
        """
        pass

    @abstractmethod
    def benchmark(self, trace: Iterable[int], frames_list: Iterable[int]) -> list:
        """
        Roda o algoritmo para vários tamanhos de molduras.
        Retorna lista de resultados para análise posterior.
        """
        pass

    @abstractmethod
    def plot(self) -> None:
        """
        Plota o gráfico com base nos resultados do benchmark.
        """
        pass