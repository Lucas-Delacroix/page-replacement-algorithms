#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
MAINS_DIR="${MAINS_DIR:-mains}"
OUT_DIR="${OUT_DIR:-results}"
TS="$(date +'%Y%m%d-%H%M%S')"
LOG_DIR="${OUT_DIR}/logs-${TS}"

SCENARIOS=(
  "main_trio_random.py"
  "main_trio_locality.py"
  "main_clock_random.py"
  "main_clock_locality.py"
  "main_contadores_random.py"
  "main_contadores_locality.py"
  "main_ws_random.py"
  "main_ws_locality.py"
)

usage() {
  cat <<EOF
Uso: $(basename "$0") [--clean] [--python PYTHON] [--mains-dir DIR] [--out-dir DIR]

Opções:
  --clean             Remove saídas antigas de results/ (mantém logs e novas execuções).
  --python PYTHON     Binário do Python (default: python3)
  --mains-dir DIR     Diretório onde estão os main_*.py (default: mains)
  --out-dir DIR       Diretório base de saída (default: results)
EOF
}

ensure_dirs() {
  mkdir -p "${OUT_DIR}" "${LOG_DIR}"
}

clean_outputs() {
  echo "[clean] Removendo saídas anteriores em '${OUT_DIR}'..."
  find "${OUT_DIR}" -type f \( -name "*.png" -o -name "*.csv" \) -delete || true
  find "${OUT_DIR}/single" -mindepth 1 -type f -delete 2>/dev/null || true
  find "${OUT_DIR}/comparison" -mindepth 1 -type f -delete 2>/dev/null || true
  find "${OUT_DIR}/reports" -mindepth 1 -type f -delete 2>/dev/null || true
  echo "[clean] OK."
}

run_one() {
  local main_py="$1"
  local name="${main_py%.py}"
  local log_file="${LOG_DIR}/${name}.log"

  echo "[run] ${main_py}"
  set +e
  "${PYTHON_BIN}" "${MAINS_DIR}/${main_py}" >"${log_file}" 2>&1
  local status=$?
  set -e

  if [[ ${status} -ne 0 ]]; then
    echo "[fail] ${main_py} (status=${status}) — veja o log: ${log_file}"
    return ${status}
  fi

  echo "[ok] ${main_py} — log: ${log_file}"
}

CLEAN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --clean)
      CLEAN=true
      shift
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --mains-dir)
      MAINS_DIR="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage; exit 0
      ;;
    *)
      echo "Opção desconhecida: $1"; usage; exit 1
      ;;
  esac
done

ensure_dirs
$CLEAN && clean_outputs

echo "[info] Python: ${PYTHON_BIN}"
echo "[info] Mains Dir: ${MAINS_DIR}"
echo "[info] Out Dir: ${OUT_DIR}"
echo "[info] Logs: ${LOG_DIR}"
echo


if [[ ! -d "${MAINS_DIR}" ]]; then
  echo "[erro] Diretório '${MAINS_DIR}' não existe." >&2
  exit 1
fi

fail_count=0
for m in "${SCENARIOS[@]}"; do
  if [[ ! -f "${MAINS_DIR}/${m}" ]]; then
    echo "[warn] ${MAINS_DIR}/${m} não encontrado. Pulando."
    continue
  fi
  if ! run_one "${m}"; then
    ((fail_count++)) || true
  fi
done

echo
if [[ ${fail_count} -gt 0 ]]; then
  echo "[done] Concluído com ${fail_count} falha(s). Consulte os logs em: ${LOG_DIR}"
  exit 1
else
  echo "[done] Todos os cenários executados com sucesso. Logs: ${LOG_DIR}"
fi
