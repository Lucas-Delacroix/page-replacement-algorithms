from src.algorithms.second_chance import SecondChance
from src.core import Access
from src.algorithms.fifo import Fifo
from src.algorithms.clock import Clock

def make_sample_trace():
    pages = [1, 2, 3, 2, 4, 1, 5, 2, 1, 2, 3, 4, 5]
    writes = {4, 7, 11}
    return [Access(page_id=pid, write=(i in writes), t=i) for i, pid in enumerate(pages)]

def main():
    trace = make_sample_trace()
    frames_list = [2, 3, 4]

    algos = [Fifo(), SecondChance(), Clock()]
    for algo in algos:
        br = algo.benchmark(trace, frames_list)
        algo.plot(f"{algo.name}.png")



if __name__ == "__main__":
    main()
