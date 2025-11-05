from src.page import Page
from src.access import Access
from src.algorithms.fifo import Fifo
from src.plot import plot_comparison

def make_trace():
    p1, p2, p3, p4, p5 = Page(1), Page(2), Page(3), Page(4), Page(5)
    return [
        Access(p1), Access(p2), Access(p3), Access(p4),
        Access(p1, bit_r=1), Access(p2, bit_r=1),
        Access(p5), Access(p1),
        Access(p2), Access(p3), Access(p4), Access(p5, bit_m=1),
    ]

def main():
    trace = make_trace()
    frames_list = [2, 3, 4, 5]

    fifo = Fifo()
    br_fifo = fifo.benchmark(trace, frames_list)
    fifo.plot(save_path="fifo.png", show=False)

if __name__ == "__main__":
    main()
