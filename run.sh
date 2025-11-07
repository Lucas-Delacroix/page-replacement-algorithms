#!/usr/bin/env bash
set -euo pipefail

# ---- Raiz do projeto (pasta onde este script está) ----
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

# ---- Garante que 'src' é importável ----
export PYTHONPATH="${ROOT_DIR}:${PYTHONPATH:-}"

# ---- Python (ajuste se usa venv) ----
PY="${PYTHON_BIN:-python3}"

# ---- Diretório dos mains ----
MAINS_DIR="${MAINS_DIR:-mains}"

# ---- Cenários disponíveis ----
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
  echo "Uso: $(basename "$0") [all | nome_do_arquivo.py]"
  echo
  echo "Exemplos:"
  echo "  ./run.sh all                          # roda todos"
  echo "  ./run.sh main_trio_random.py          # roda só esse"
  echo
  echo "Variáveis úteis:"
  echo "  PYTHON_BIN=/caminho/venv/bin/python   ./run.sh all"
  echo "  MAINS_DIR=outros_mains                ./run.sh all"
}

run_one() {
  local file="$1"
  if [[ ! -f "${MAINS_DIR}/${file}" ]]; then
    echo "[erro] Não achei ${MAINS_DIR}/${file}"
    exit 1
  fi
  echo "[run] ${MAINS_DIR}/${file}"
  "${PY}" "${MAINS_DIR}/${file}"
  echo "[ok]  ${file}"
}

if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

case "$1" in
  all)
    for sc in "${SCENARIOS[@]}"; do
      run_one "$sc"
    done
    ;;
  -h|--help)
    usage
    ;;
  *)
    run_one "$1"
    ;;
esac
