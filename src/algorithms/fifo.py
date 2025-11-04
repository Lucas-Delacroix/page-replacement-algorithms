from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult, BenchmarkResult

class Fifo(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("FIFO")

    def run(self):