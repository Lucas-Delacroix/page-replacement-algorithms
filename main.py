from src.algorithms.LRU import LRU
from src.algorithms.NFU import NFU
from src.algorithms.second_chance import SecondChance
from src.algorithms.fifo import Fifo
from src.algorithms.clock import Clock
from src.algorithms.nru import NRU
from src.algorithms.working_set import WorkingSet
from src.algorithms.wsclock import WSClock
from src.algorithms.Aging import Aging
from src.algorithms.Optimal import Optimal
from src.core import make_random_trace
from src.plot import plot_faults, plot_hits, plot_fault_rate, plot_hit_rate
from src.reports import export_benchmark_csv


def main():
    trace, frames_list = make_random_trace(num_pages=15, frames=None, frame_mode="auto", seed=42)

    algos = [
        Fifo(),
        SecondChance(),
        Clock(),
        NFU(),
        LRU(),
        NRU(),
        WorkingSet(window=4),
        WSClock(window=4),
        Aging(bits=8, refresh_every=1),
        Optimal()
    ]
    benchmarks = []
    for algo in algos:
        br = algo.benchmark(trace, frames_list)
        benchmarks.append(br)
        algo.plot(f"{algo.name}.png")

    plot_faults(benchmarks)
    plot_hits(benchmarks)
    plot_fault_rate(benchmarks)
    plot_hit_rate(benchmarks)

    export_benchmark_csv(
        benchmarks,
        out_dir="results/reports",
        summary_filename="benchmark_summary.csv",
        detailed_filename="benchmark_detailed.csv",
        sort_by="avg_faults",
    )


if __name__ == "__main__":
    main()
