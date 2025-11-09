from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import csv
import os
import matplotlib.pyplot as plt
import numpy as np


# Estruturas de rastreamento (NÃO fazem I/O)
# ============================================================
# ============================================================

@dataclass(frozen=True)
class FrameSnapshot:
    """
    Foto de um frame após processar um acesso.

    frame_index: índice do frame (0..frames-1)
    page_id: página residente (None = vazio)
    R, M: bits de referência/modificação (se o algoritmo usar)
    meta: extras específicos do algoritmo (ex.: ponteiro do Clock, idade, etc.)
    """
    frame_index: int
    page_id: Optional[int]
    R: int = 0
    M: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepLog:
    """
    Um passo da execução (um acesso do traço).

    t: índice do acesso (0,1,2,...)
    access_page: página requisitada
    access_write: True = escrita, False = leitura
    hit: True se estava na memória
    evicted_page: página expulsa neste passo (se houver)
    decision_meta: infos sobre a decisão (ex.: policy, ponteiro, etc.)
    frames_after: estado de todos os frames após o acesso
    """
    t: int
    access_page: int
    access_write: bool
    hit: bool
    evicted_page: Optional[int]
    decision_meta: Dict[str, Any]
    frames_after: List[FrameSnapshot]


@dataclass
class RunTrace:
    """
    Linha do tempo completa de UMA execução de um algoritmo
    para um dado número de frames.
    """
    algo_name: str
    frames: int
    steps: List[StepLog] = field(default_factory=list)

    @property
    def num_steps(self) -> int:
        return len(self.steps)

    def to_rows(self) -> List[Dict[str, Any]]:
        """
        Achata em linhas para CSV:
        - colunas gerais: t, access_page, access_write, hit, evicted_page
        - colunas por frame: F<i>_page, F<i>_R, F<i>_M, F<i>_meta_<k>
        - colunas de decisão: decision_<k>
        """
        rows: List[Dict[str, Any]] = []

        for s in self.steps:
            base: Dict[str, Any] = {
                "t": s.t,
                "access_page": s.access_page,
                "access_write": int(s.access_write),
                "hit": int(s.hit),
                "evicted_page": "" if s.evicted_page is None else s.evicted_page,
            }

            # Estado dos frames
            for fs in s.frames_after:
                base[f"F{fs.frame_index}_page"] = "" if fs.page_id is None else fs.page_id
                base[f"F{fs.frame_index}_R"] = fs.R
                base[f"F{fs.frame_index}_M"] = fs.M
                for k, v in (fs.meta or {}).items():
                    base[f"F{fs.frame_index}_meta_{k}"] = v

            # Decisão da política
            for k, v in (s.decision_meta or {}).items():
                base[f"decision_{k}"] = v

            rows.append(base)

        return rows


# ============================================================
# Exportação: CSV
# ============================================================

def export_run_trace_csv(run_trace: RunTrace, out_path: str) -> str:
    """
    Exporta um RunTrace para um CSV DIDÁTICO e ENXUTO, no formato:

        t, pagina_pedida, hit_fault, pagina_expulsa, frames

    Exemplo de linha:
        0, 4, fault, -, [4, -, -]
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Cabeçalho simples, em português
        writer.writerow(["t", "page_requested", "hit_fault", "expulsed_page", "frames"])

        for step in run_trace.steps:
            # Ordena os snapshots por índice de frame (0,1,2,...)
            frames_ordered = sorted(step.frames_after, key=lambda fs: fs.frame_index)

            # Representação dos frames: [p0, p1, p2, ...] com "-" para vazios
            frames_repr = "[" + ", ".join(
                (str(fs.page_id) if fs.page_id is not None else "-")
                for fs in frames_ordered
            ) + "]"

            hit_fault = "hit" if step.hit else "fault"
            evicted = step.evicted_page if step.evicted_page is not None else "-"

            writer.writerow([
                step.t,
                step.access_page,
                hit_fault,
                evicted,
                frames_repr,
            ])

    print(f"[trace] CSV (simplificado) gerado: {out_path}")
    return out_path


# ============================================================
# Exportação: diagrama tipo Gantt (ocupação dos frames)
# ============================================================

def _build_frame_matrix_and_faults(run_trace: RunTrace) -> Tuple[np.ndarray, List[int]]:
    """
    Retorna:
      - matriz (F x T) com page_id em cada frame/tempo (0 = vazio)
      - lista de tempos t onde houve fault
    """
    T = run_trace.num_steps
    F = run_trace.frames

    mat = np.zeros((F, T), dtype=int)
    faults_t: List[int] = []

    for s in run_trace.steps:
        for fs in s.frames_after:
            mat[fs.frame_index, s.t] = 0 if fs.page_id is None else int(fs.page_id)
        if not s.hit:
            faults_t.append(s.t)

    return mat, faults_t


def plot_frames_gantt(
    run_trace: RunTrace,
    *,
    annotate_pages: bool = True,
    min_block_width_for_label: int = 4,
    save_path: Optional[str] = None,
    show: bool = False,
) -> None:
    """
    Gera um Gantt:
      - X: tempo (t)
      - Y: frames (0 no topo)
      - blocos contínuos = mesma página no mesmo frame
      - faults marcados no topo
    """
    T = run_trace.num_steps
    F = run_trace.frames
    if T == 0 or F == 0:
        return

    mat, faults_t = _build_frame_matrix_and_faults(run_trace)

    fig_w = max(10.0, T / 10.0)
    fig_h = 1.2 * F + 2.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    y_height = 0.8
    y_gap = 0.4

    def color_for(pid: int):
        if pid == 0:
            return None
        frac = (pid * 0.6180339887) % 1.0
        return plt.cm.hsv(frac)

    for f in range(F):
        row = mat[f, :]
        y_base = f * (y_height + y_gap)
        t = 0

        while t < T:
            pid = row[t]
            start = t
            while t + 1 < T and row[t + 1] == pid:
                t += 1
            end = t
            length = end - start + 1

            if pid != 0:
                ax.broken_barh(
                    [(start, length)],
                    (y_base, y_height),
                    facecolors=[color_for(pid)],
                    edgecolors="black",
                    linewidth=0.6,
                )
                if annotate_pages and length >= min_block_width_for_label:
                    ax.text(
                        start + length / 2.0,
                        y_base + y_height / 2.0,
                        str(pid),
                        ha="center",
                        va="center",
                        fontsize=8,
                    )
            else:
                ax.broken_barh(
                    [(start, length)],
                    (y_base, y_height),
                    facecolors="none",
                    edgecolors="lightgray",
                    linewidth=0.3,
                )

            t += 1

    ax.set_ylim(-y_gap, F * (y_height + y_gap))
    ax.set_xlim(0, T)
    ax.set_xlabel("t (acessos)")
    ax.set_ylabel("frames (0 no topo)")
    ax.set_yticks(
        [i * (y_height + y_gap) + y_height / 2.0 for i in range(F)]
    )
    ax.set_yticklabels([str(i) for i in range(F)])
    ax.set_title(f"{run_trace.algo_name} — Gantt de Ocupação dos Frames (F={F})")
    ax.grid(True, axis="x", linestyle="--", linewidth=0.5, alpha=0.5)

    top = F * (y_height + y_gap)
    for ft in faults_t:
        ax.plot([ft, ft], [top, top + 0.6], linestyle="-", linewidth=0.8)
        ax.plot(ft, top + 0.6, marker="v")

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"[trace] Gantt salvo em: {save_path}")

    if show:
        plt.show()
    else:
        plt.close()