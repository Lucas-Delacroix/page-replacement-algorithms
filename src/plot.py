import matplotlib.pyplot as plt
from typing import List

from src.algorithms.baseAlgorithm import BenchmarkResult

def plot_faults(benchmarks: List[BenchmarkResult]) -> None:
    plt.figure()
    for br in benchmarks:
        frames = [r.frames for r in br.results]
        faults = [r.faults for r in br.results]
        plt.plot(frames, faults, marker="o", label=br.algo_name)
    plt.xlabel("Frames")
    plt.ylabel("Faltas de página")
    plt.title("Comparação — Faltas de página")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_hits(benchmarks: List[BenchmarkResult]) -> None:
    plt.figure()
    for br in benchmarks:
        frames = [r.frames for r in br.results]
        hits = [r.hits for r in br.results]
        plt.plot(frames, hits, marker="o", label=br.algo_name)
    plt.xlabel("Frames")
    plt.ylabel("Acertos de página")
    plt.title("Comparação — Acertos de página")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_fault_rate(benchmarks: List[BenchmarkResult]) -> None:
    plt.figure()
    for br in benchmarks:
        frames = [r.frames for r in br.results]
        rates = [r.fault_rate for r in br.results]
        plt.plot(frames, rates, marker="o", label=br.algo_name)
    plt.xlabel("Frames")
    plt.ylabel("Taxa de faltas")
    plt.title("Comparação — Taxa de faltas")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_hit_rate(benchmarks: List[BenchmarkResult]) -> None:
    plt.figure()
    for br in benchmarks:
        frames = [r.frames for r in br.results]
        rates = [r.hit_rate for r in br.results]
        plt.plot(frames, rates, marker="o", label=br.algo_name)
    plt.xlabel("Frames")
    plt.ylabel("Taxa de acertos")
    plt.title("Comparação — Taxa de acertos")
    plt.legend()
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


def plot_comparison(benchmarks: List[BenchmarkResult], metric: str = "faults") -> None:
    """
    Plota a comparação de N algoritmos no mesmo gráfico.
    :param benchmarks: lista de BenchmarkResult (um para cada algoritmo)
    :param metric: "faults", "hits", "fault_rate" ou "hit_rate"
    """
    if metric == "faults":
        plot_faults(benchmarks)
    elif metric == "hits":
        plot_hits(benchmarks)
    elif metric == "fault_rate":
        plot_fault_rate(benchmarks)
    elif metric == "hit_rate":
        plot_hit_rate(benchmarks)
    else:
        raise ValueError("Métrica inválida. Use 'faults', 'hits', 'fault_rate' ou 'hit_rate'.")
