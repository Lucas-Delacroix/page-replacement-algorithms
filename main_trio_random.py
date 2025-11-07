from src.algorithms.fifo import Fifo
from src.algorithms.LRU import LRU
from src.algorithms.Optimal import Optimal
from src.core import make_random_trace
from src.plot import plot_faults, plot_hits, plot_fault_rate, plot_hit_rate
from src.reports import export_benchmark_csv

def main():
    NUM_PAGES = 60
    TRACE_LEN = 800
    WRITE_PROB = 0.25
    SEED = 42

    trace, frames_list = make_random_trace(
        num_pages=NUM_PAGES,
        trace_length=TRACE_LEN,
        write_prob=WRITE_PROB,
        frames=None,
        frame_mode="auto",
        seed=SEED,
    )

    algos = [Fifo(), LRU(), Optimal()]
    benchmarks = [algo.benchmark(trace, frames_list) for algo in algos]
    for algo in algos:
        algo.plot(f"TRIO-RANDOM-{algo.name}.png")

    plot_faults(benchmarks); plot_hits(benchmarks)
    plot_fault_rate(benchmarks); plot_hit_rate(benchmarks)

    export_benchmark_csv(
        benchmarks,
        out_dir="results/reports/TRIO",
        summary_filename="TRIO_RANDOM_summary.csv",
        detailed_filename="TRIO_RANDOM_detailed.csv",
        sort_by="avg_faults",
    )

if __name__ == "__main__":
    main()