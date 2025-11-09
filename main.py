from src.algorithms.fifo import Fifo
from src.core import make_locality_trace
from src.plot import plot_faults, plot_hits, plot_fault_rate, plot_hit_rate
from src.reports import export_benchmark_csv
from src.trace_exporter import TraceExporter


def main() -> None:
    trace, frames_list = make_locality_trace(
        num_pages=10,
        trace_length=40,
        locality_prob=0.9,
        phase_length=10,
        working_set_size=3,
        seed=1,
    )

    frames_list = [40]

    algos = [
        Fifo(),
    ]

    benchmarks = []

    for algo in algos:
        br = algo.benchmark(
            trace,
            frames_list,
        )

        benchmarks.append(br)

        algo.plot(f"{algo.name}.png")

        TraceExporter.export_all(
            algo_name=algo.name,
            traces_by_frames=algo.last_traces,
            out_dir="results/trace_didatico"
        )

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
