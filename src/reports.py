import csv
import os
from typing import Dict, List, Tuple
from src.core import BenchmarkResult, RunResult

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _avg(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _compute_algo_summary(br: BenchmarkResult) -> Dict[str, object]:
    """
    Calcula métricas agregadas por algoritmo a partir do BenchmarkResult.
    Retorna um dicionário pronto para serialização em CSV.
    """
    results: List[RunResult] = br.results
    frames = [r.frames for r in results]
    faults = [r.faults for r in results]
    hits = [r.hits for r in results]
    evictions = [r.evictions for r in results]
    fault_rates = [r.fault_rate for r in results]
    hit_rates = [r.hit_rate for r in results]

    minF = min(frames) if frames else None
    maxF = max(frames) if frames else None
    faults_at_minF = next((r.faults for r in results if r.frames == minF), None)
    faults_at_maxF = next((r.faults for r in results if r.frames == maxF), None)

    return {
        "algo_name": br.algo_name,
        "avg_faults": float(_avg(faults)),
        "avg_fault_rate": float(_avg(fault_rates)),
        "avg_hits": float(_avg(hits)),
        "avg_hit_rate": float(_avg(hit_rates)),
        "avg_evictions": float(_avg(evictions)),
        "min_frames": minF,
        "max_frames": maxF,
        "faults_at_minF": faults_at_minF,
        "faults_at_maxF": faults_at_maxF,
    }


def _pick_optimal_baseline(summaries: List[Dict[str, object]]) -> Dict[str, object]:
    """
    Seleciona a baseline SEMPRE como o algoritmo Ótimo.
    Aceita variações de nome: 'Ótimo', 'Otimo', 'Optimal' (case-insensitive).
    Se não encontrar, cai no menor avg_faults como fallback.
    """
    if not summaries:
        raise ValueError("Nenhum resumo disponível para selecionar baseline.")

    aliases = {"ótimo", "otimo", "optimal"}
    for s in summaries:
        name = str(s.get("algo_name", "")).strip().lower()
        if name in aliases:
            return s

    return min(summaries, key=lambda s: s["avg_faults"])


def _add_relative_columns_vs_optimal(
    summaries: List[Dict[str, object]],
    baseline_summary: Dict[str, object],
) -> None:
    """
    Adiciona colunas de comparação relativas ao Ótimo.
    Fórmula (faltas): (Ótimo - Algo) / Ótimo * 100
    Fórmula (hits):   (Algo - Ótimo) / Ótimo * 100   (maior é melhor)
    """
    base_faults = float(baseline_summary.get("avg_faults", 0.0))
    base_hits = float(baseline_summary.get("avg_hits", 0.0))

    for s in summaries:
        f = float(s.get("avg_faults", 0.0))
        h = float(s.get("avg_hits", 0.0))

        if base_faults > 0:
            s["Δ% vs Ótimo_faults"] = ((base_faults - f) / base_faults) * 100.0
        else:
            s["Δ% vs Ótimo_faults"] = 0.0

        if base_hits > 0:
            s["Δ% vs Ótimo_hits"] = ((h - base_hits) / base_hits) * 100.0
        else:
            s["Δ% vs Ótimo_hits"] = 0.0

def export_benchmark_csv(
    benchmarks: List[BenchmarkResult],
    out_dir: str = "results/reports",
    summary_filename: str = "benchmark_summary.csv",
    detailed_filename: str = "benchmark_detailed.csv",
    sort_by: str = "avg_faults",
) -> Tuple[str, str]:
    """
    Exporta dois CSVs:
      1) Resumo por algoritmo (médias, min/max, Δ% vs Ótimo).
      2) Detalhe por frame (uma linha por 'algo x frames').

    - A baseline é SEMPRE o algoritmo Ótimo (com tolerância a nomes).
    - Em caso de ausência do Ótimo, usa-se o menor avg_faults como fallback.
    """
    if not benchmarks:
        raise ValueError("A lista de benchmarks está vazia.")

    _ensure_dir(out_dir)

    summaries = [_compute_algo_summary(br) for br in benchmarks]
    optimal = _pick_optimal_baseline(summaries)
    _add_relative_columns_vs_optimal(summaries, optimal)

    if sort_by not in summaries[0]:
        raise ValueError(f"Campo sort_by inválido: {sort_by}")
    summaries_sorted = sorted(summaries, key=lambda s: s[sort_by])

    summary_headers = [
        "algo_name",
        "avg_faults",
        "avg_fault_rate",
        "avg_hits",
        "avg_hit_rate",
        "avg_evictions",
        "min_frames",
        "max_frames",
        "faults_at_minF",
        "faults_at_maxF",
        "Δ% vs Ótimo_faults",
        "Δ% vs Ótimo_hits",
    ]

    summary_path = os.path.join(out_dir, summary_filename)
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary_headers)
        writer.writeheader()
        for row in summaries_sorted:
            writer.writerow({k: row.get(k, "") for k in summary_headers})

    detailed_headers = [
        "algo_name",
        "frames",
        "faults",
        "hits",
        "evictions",
        "hit_rate",
        "fault_rate",
    ]

    detailed_path = os.path.join(out_dir, detailed_filename)
    with open(detailed_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=detailed_headers)
        writer.writeheader()
        for br in benchmarks:
            for r in br.results:
                writer.writerow({
                    "algo_name": br.algo_name,
                    "frames": r.frames,
                    "faults": r.faults,
                    "hits": r.hits,
                    "evictions": r.evictions,
                    "hit_rate": f"{r.hit_rate:.6f}",
                    "fault_rate": f"{r.fault_rate:.6f}",
                })

    print(f"[report] CSVs gerados:\n  - {summary_path}\n  - {detailed_path}")
    return summary_path, detailed_path
