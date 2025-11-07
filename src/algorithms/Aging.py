from typing import Iterable, List, Optional, Dict
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm
from src.core import Access, PTE, RunResult

class Aging(PageReplacementAlgorithm):
    def __init__(self, bits: int = 8, refresh_every: int = 1):
        """
        bits: largura do contador de envelhecimento (>=2).
        refresh_every: a cada quantas referências aplicar o 'tick' do aging.
        """
        super().__init__("Envelhecimento")
        if bits < 2:
            raise ValueError("bits deve ser >= 2")
        if refresh_every < 1:
            raise ValueError("refresh_every deve ser >= 1")
        self.bits = bits
        self.refresh_every = refresh_every

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        seq = self._normalize_trace(trace)
        mask = (1 << self.bits) - 1

        slots = [
            {"page_id": None, "counter": 0, "R": 0, "M": 0, "loaded_at": 0}
            for _ in range(frames)
        ]
        page_to_idx: Dict[int, int] = {}

        hits = faults = evictions = 0
        t = 0

        def aging_tick():
            for fr in slots:
                if fr["page_id"] is None:
                    fr["counter"] = 0
                    fr["R"] = 0
                else:
                    fr["counter"] = ((fr["R"] << (self.bits - 1)) | (fr["counter"] >> 1)) & mask
                    fr["R"] = 0

        for access in seq:
            t += 1
            pid = access.page_id
            idx = page_to_idx.get(pid)

            if idx is not None and slots[idx]["page_id"] == pid:
                hits += 1
                slots[idx]["R"] = 1
                if access.write:
                    slots[idx]["M"] = 1
            else:
                faults += 1

                free = next((i for i, fr in enumerate(slots) if fr["page_id"] is None), None)
                if free is not None:
                    slots[free].update(page_id=pid, counter=0, R=1, M=int(access.write), loaded_at=t)
                    page_to_idx[pid] = free
                else:
                    victim = min(
                        range(frames),
                        key=lambda i: (slots[i]["counter"], slots[i]["loaded_at"])
                    )
                    old_pid = slots[victim]["page_id"]
                    if old_pid in page_to_idx:
                        del page_to_idx[old_pid]

                    slots[victim].update(page_id=pid, counter=0, R=1, M=int(access.write), loaded_at=t)
                    page_to_idx[pid] = victim
                    evictions += 1

            if (t % self.refresh_every) == 0:
                aging_tick()

        total = len(seq)
        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=total,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )