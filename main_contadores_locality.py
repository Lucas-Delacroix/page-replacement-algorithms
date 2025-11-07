from src.algorithms.NFU import NFU
from src.algorithms.Aging import Aging
from src.algorithms.Optimal import Optimal
from src.core import make_locality_trace
from src.plot import plot_faults, plot_hits, plot_fault_rate, plot_hit_rate
from src.reports import export_benchmark_csv

def main():
    NUM_PAGES = 60
    TRACE_LEN = 800
    WRITE_PROB = 0.25
    SEED = 42

    LOCALITY_PROB = 0.85
    PHASE_LEN = 80
    WS_SIZE = 8

    trace, frames_list = make_locality_trace(
        num_pages=NUM_PAGES,
        trace_length=TRACE_LEN,
        write_prob=WRITE_PROB,
        locality_prob=LOCALITY_PROB,
        phase_length=PHASE_LEN,
        working_set_size=WS_SIZE,
        seed=SEED,
    )

    algos = [NFU(), Aging(bits=8, refresh_every=1), Optimal()]
    benchmarks = [algo.benchmark(trace, frames_list) for algo in algos]
    for algo in algos:
        algo.plot(f"COUNT-LOCALITY-{algo.name}.png")

    plot_faults(benchmarks); plot_hits(benchmarks)
    plot_fault_rate(benchmarks); plot_hit_rate(benchmarks)

    export_benchmark_csv(
        benchmarks,
        out_dir="results/reports/COUNT",
        summary_filename="COUNT_LOCALITY_summary.csv",
        detailed_filename="COUNT_LOCALITY_detailed.csv",
        sort_by="avg_faults",
    )

if __name__ == "__main__":
    main()
