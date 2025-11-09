from typing import Dict
import os
from src.trace import RunTrace, export_run_trace_csv, plot_frames_gantt


class TraceExporter:
    """
    Responsável por exportar RunTrace para arquivos.
    """

    @staticmethod
    def export_all(
        algo_name: str,
        traces_by_frames: Dict[int, RunTrace],
        out_dir: str,
        *,
        export_csv: bool = True,
        export_gantt: bool = True,
    ) -> None:
        if not traces_by_frames:
            print(f"[trace] Nenhum trace para exportar ({algo_name}).")
            return

        os.makedirs(out_dir, exist_ok=True)

        for frames, run_trace in traces_by_frames.items():
            prefix = f"{algo_name}_F{frames}"

            if export_csv:
                csv_path = os.path.join(out_dir, f"{prefix}.csv")
                export_run_trace_csv(run_trace, csv_path)

            if export_gantt:
                gantt_path = os.path.join(out_dir, f"{prefix}_gantt.png")
                plot_frames_gantt(run_trace, save_path=gantt_path, show=False)
