import os
import matplotlib.pyplot as plt
from typing import List, Optional
from src.algorithms.baseAlgorithm import BenchmarkResult

def _plot_many(
    benchmarks: List[BenchmarkResult],
    metric: str,
    title: str,
    save_path: Optional[str] = None,
    show: bool = True,
):
    os.makedirs("results", exist_ok=True)
    save_path = f"results/{save_path}"
    fig, ax = plt.subplots()
    for br in benchmarks:
        frames = [r.frames for r in br.results]
        if metric == "faults":
            ys = [r.faults for r in br.results]
        elif metric == "hits":
            ys = [r.hits for r in br.results]
        elif metric == "fault_rate":
            ys = [r.fault_rate for r in br.results]
        elif metric == "hit_rate":
            ys = [r.hit_rate for r in br.results]
        else:
            raise ValueError("Métrica inválida. Use faults/hits/fault_rate/hit_rate.")
        ax.plot(frames, ys, marker="o", label=br.algo_name)

    ax.set_xlabel("Frames")
    ylabels = {
        "faults": "Faltas de página",
        "hits": "Acertos de página",
        "fault_rate": "Taxa de faltas",
        "hit_rate": "Taxa de acertos",
    }
    ax.set_ylabel(ylabels[metric])
    ax.set_title(title)
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Gráfico salvo em: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

def plot_faults(benchmarks: List[BenchmarkResult], show: bool = False) -> None:
    _plot_many(benchmarks, "faults", "Comparação — Faltas de página", "faults", show)

def plot_hits(benchmarks: List[BenchmarkResult], show: bool = False) -> None:
    _plot_many(benchmarks, "hits", "Comparação — Acertos de página", "hits", show)

def plot_fault_rate(benchmarks: List[BenchmarkResult], show: bool = False) -> None:
    _plot_many(benchmarks, "fault_rate", "Comparação — Taxa de faltas", "fault_rate", show)

def plot_hit_rate(benchmarks: List[BenchmarkResult], show: bool = False) -> None:
    _plot_many(benchmarks, "hit_rate", "Comparação — Taxa de acertos", "hit_rate", show)

def plot_comparison(benchmarks: List[BenchmarkResult], metric: str = "faults",
                    save_path: Optional[str] = None, show: bool = False) -> None:
    if metric == "faults":
        plot_faults(benchmarks, show)
    elif metric == "hits":
        plot_hits(benchmarks, show)
    elif metric == "fault_rate":
        plot_fault_rate(benchmarks, show)
    elif metric == "hit_rate":
        plot_hit_rate(benchmarks, show)
    else:
        raise ValueError("Métrica inválida. Use 'faults', 'hits', 'fault_rate' ou 'hit_rate'.")
