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

def main():
    trace, frames_list = make_random_trace(num_pages=50, frames=None, frame_mode="auto", seed=42)

    algos = [
        Fifo(),
        SecondChance(),
        Clock(),
        NFU(),
        LRU(),
        NRU(),
        WorkingSet(window=4),
        WSClock(window=4),
        Optimal(),
        Aging(bits=8, refresh_every=1)
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



if __name__ == "__main__":
    main()
