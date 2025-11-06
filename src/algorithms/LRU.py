from typing import Iterable, Set, Dict, List
from baseAlgorithm import PageReplacementAlgorithm
from src.algorithms.baseAlgorithm import PageReplacementAlgorithm, RunResult
from src.core import Access, PTE
import matplotlib.pyplot as plt

class LRU(PageReplacementAlgorithm):
    def __init__(self):
        super().__init__("LRU")

    def run(self, trace: Iterable[Access], frames: int) -> RunResult:
        if frames <= 0:
            raise ValueError("frames deve ser > 0")

        seq = self._normalize_trace(trace)
        trace_len = len(seq)

        all_pages = {acc.page_id for acc in seq}
        page_table: Dict[int, PTE] = {
            pid: PTE(
                page_id=pid,
                frame=None,
                R=0,
                M=0,
                loaded_at=None,
                last_used=None,
            )
            for pid in all_pages
        }


        frames_list: List[PTE] = []

        faults = hits = evictions = 0

        time: int = 0

        for acc in seq:
            pte: PTE = page_table[acc.page_id]

            if pte.frame is not None:
                hits += 1
                pte.R = 1
                if acc.write:
                    pte.M = 1
                pte.last_used = time
                continue

            faults += 1

            if len(frames_list) < frames:
                pte.frame = len(frames_list)
                pte.R = 1
                pte.M = int(acc.write)
                pte.loaded_at = time
                pte.last_used = time

                frames_list.append(pte)
                continue

            victim = min_manual(frames_list, key=lambda x: x.last_used)
            evictions += 1

            victim_frame = victim.frame
            frames_list.remove(victim)
            victim.frame = None

            pte.frame = victim_frame
            pte.R = 1
            pte.M = int(acc.write)
            pte.loaded_at = time
            pte.last_used = time
            frames_list.append(pte)


        return RunResult(
            algo_name=self.name,
            frames=frames,
            trace_len=trace_len,
            faults=faults,
            hits=hits,
            evictions=evictions,
        )
    
    def plot(self, save_path: str | None = None, show: bool = False) -> None:
        if self._last_benchmark is None:
            raise RuntimeError("Sem benchmark: chame benchmark() antes de plot().")

        frames = [r.frames for r in self._last_benchmark.results]
        faults = [r.faults for r in self._last_benchmark.results]

        plt.figure()
        plt.plot(frames, faults, marker="o", label=self._last_benchmark.algo_name)
        plt.xlabel("Frames")
        plt.ylabel("Faltas de página")
        plt.title(f"{self.name.upper()} — Faltas de página")
        plt.grid(True, linestyle="--", linewidth=0.5)
        plt.legend()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Gráfico salvo em: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

def min_manual(frames_list, key=lambda x: x):
    """Retorna o elemento mínimo de frames_list com base em key (implementação manual de min)."""
    if not frames_list:
        raise ValueError("frames_list está vazia")

    menor = frames_list[0]
    menor_valor = key(menor)

    time = 0
    for item in frames_list[1:]:
        time += 1
        valor = key(item)
        if valor < menor_valor:
            menor = item
            menor_valor = valor

    return menor, time