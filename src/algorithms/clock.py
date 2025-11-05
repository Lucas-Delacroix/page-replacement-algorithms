from typing import Iterable, Set
from baseAlgorithm import PageReplacementAlgorithm
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult
from src.access import Access
from collections import deque

class Clock(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("clock")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        pointer = 0
        if frames <= 0:
            raise ValueError("frames must be greater than 0")
        
        seq = self._normalize_trace(trace)
        
        frames_list = []

        in_mem: Set[int] = set()
        faults = hits = evictions = 0
        trace_len = len(seq)

        for acc in seq:
            pid = acc.page.id

            if pid in in_mem:
                hits += 1

                for f in frames_list: # joga o bit r da página 
                    if f["pid"] == pid:
                        f["bit_r"] = 1
                        break
                continue

            faults += 1
            if len(frames_list) < frames:
                frames_list.append({"pid": pid, "bit_r": 1})
                in_mem.add(pid)
            else:
                while frames_list[pointer]["bit_r"] == 1: # zera o bit r da página mais antiga
                    frames_list[pointer]["bit_r"] = 0
                    pointer = (pointer + 1) % frames
                
                # remove página mais antiga da memória
                old_pid = frames_list[pointer]["pid"]
                in_mem.remove(old_pid)
                evictions += 1
    
                # adiciona página nova na memória
                frames_list[pointer] = {"pid": pid, "bit_r": 1}
                in_mem.add(pid)
                pointer = (pointer + 1) % frames

        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )