from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Union, Tuple
import random

def make_random_trace(
    num_pages: int = 10,
    trace_length: int = 50,
    write_prob: float = 0.3,
    frames: Union[Tuple[int, int], List[int], int, None] = None,
    frame_mode: str = "auto",
    seed: Optional[int] = None,
) -> tuple[List[Access], List[int]]:
    """
    Gera um traço aleatório e a lista de quantidades de molduras (frames).
    frames:
      - (min,max)  -> gera range(min, max+1)
      - [a,b,c]    -> usa lista fixa [a,b,c]
      - k (int)    -> usa [k]
      - None       -> calcula via frame_mode ("auto"|"range"|"fixed")
    Retorna:
      (trace, frames_list)
    """

    if num_pages < 1:
        raise ValueError("num_pages deve ser >= 1.")
    if trace_length < 0:
        raise ValueError("trace_length deve ser >= 0.")
    if not (0.0 <= write_prob <= 1.0):
        raise ValueError("write_prob deve estar em [0.0, 1.0].")

    if seed is not None:
        random.seed(seed)

    pages = list(range(1, num_pages + 1))
    trace: List[Access] = []
    for t in range(trace_length):
        pid = random.choice(pages)
        write = random.random() < write_prob
        trace.append(Access(page_id=pid, write=write, t=t))

    def ensure_positive(v: int, name: str) -> int:
        if v <= 0:
            raise ValueError(f"{name} deve ser > 0.")
        return v

    frames_list: List[int]

    if isinstance(frames, tuple):
        if len(frames) != 2:
            raise ValueError("frames (tupla) deve ser (min, max).")
        start, end = frames
        start = ensure_positive(start, "frames.min")
        end = ensure_positive(end, "frames.max")
        if start > end:
            raise ValueError("frames (min,max): min não pode ser > max.")
        frames_list = list(range(start, end + 1))

    elif isinstance(frames, list):
        if not frames:
            raise ValueError("frames (lista) não pode ser vazia.")
        frames_list = sorted({ensure_positive(x, "frames[i]") for x in frames})

    elif isinstance(frames, int):
        frames_list = [ensure_positive(frames, "frames")]

    elif frames is None:
        if frame_mode == "auto":
            min_f = max(1, num_pages // 5)
            max_f = max(min_f + 1, (num_pages * 4) // 5 or 1)
            step = max(1, (max_f - min_f) // 4)
            frames_list = list(range(min_f, max_f + 1, step))
            if frames_list[-1] != max_f:
                frames_list.append(max_f)

        elif frame_mode == "range":
            start, end = 2, max(2, min(8, num_pages))
            if start > end:
                start, end = 1, max(1, num_pages)
            frames_list = list(range(start, end + 1))

        elif frame_mode == "fixed":
            raise ValueError("frame_mode='fixed' requer frames=list[int].")
        else:
            raise ValueError("frame_mode inválido. Use 'auto', 'range' ou 'fixed'.")

    else:
        raise ValueError("Tipo de 'frames' inválido.")

    return trace, frames_list

@dataclass(frozen=True)
class Access:
    """Evento de acesso a uma página.
    - page_id: identificador lógico da página
    - write: True se for escrita (pode sujar a página), False se leitura
    - t: timestamp opcional (útil para LRU exato ou logs)
    """
    page_id: int
    write: bool = False
    t: Optional[int] = None


@dataclass(frozen=True)
class RunResult:
    algo_name: str
    frames: int
    trace_len: int
    faults: int
    hits: int
    evictions: int

    @property
    def hit_rate(self) -> float:
        return self.hits / self.trace_len if self.trace_len else 0.0

    @property
    def fault_rate(self) -> float:
        return self.faults / self.trace_len if self.trace_len else 0.0


@dataclass
class BenchmarkResult:
    algo_name: str
    results: List[RunResult]


@dataclass
class PTE:
    """Entrada de tabela de páginas simplificada (estado residente)."""
    page_id: int
    frame: int
    R: int = 0
    M: int = 0
    loaded_at: int = 0
    last_used: int = 0
