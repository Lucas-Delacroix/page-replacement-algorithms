from src.algorithms.second_chance import SecondChance
from src.core import Access, make_random_trace
from src.algorithms.fifo import Fifo
from src.algorithms.clock import Clock
from src.plot import *


def main():
    trace, frames_list = make_random_trace(num_pages=50, frames=None, frame_mode="auto", seed=42)

    benchmarks = []
    algos = [Fifo(), SecondChance(), Clock()]
    for algo in algos:
        br = algo.benchmark(trace, frames_list)
        benchmarks.append(br)
        algo.plot(f"{algo.name}.png")

    plot_faults(benchmarks)
    plot_hits(benchmarks)
    plot_fault_rate(benchmarks)
    plot_hit_rate(benchmarks)



if __name__ == "__main__":
    main()
