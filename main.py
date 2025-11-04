from src.algorithms.fifo import Fifo
from src.algorithms.baseAlgorithm import BenchmarkResult
from src.plot import plot_comparison

def main():
    # Exemplo de traço de referência de páginas
    trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    # Lista de quantidades de frames para o benchmark
    frames_list = [2, 3, 4, 5]

    fifo = Fifo()
    benchmark_result: BenchmarkResult = fifo.benchmark(trace, frames_list)
    fifo.plot('fifo')

if __name__ == "__main__":
    main()
