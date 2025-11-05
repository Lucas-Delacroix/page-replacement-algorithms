from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

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
