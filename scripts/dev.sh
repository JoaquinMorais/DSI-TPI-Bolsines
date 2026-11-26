#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"
VENV_DIR="$ROOT_DIR/.venv"
DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///$ROOT_DIR/backend/data/bolsines.db}"
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:$FRONTEND_PORT}"
export VITE_API_URL="${VITE_API_URL:-http://localhost:$BACKEND_PORT}"

echo "Bolsines - entorno de desarrollo"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "No se encontro $PYTHON_BIN. Instala Python 3.12 o define PYTHON_BIN." >&2
  exit 1
fi
if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 12) else 1)'; then
  echo "Se requiere Python 3.12 o superior." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creando entorno virtual en .venv..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r backend/requirements.txt

if ! command -v node >/dev/null 2>&1; then
  echo "No se encontro Node.js. Instala Node 18 o superior." >&2
  exit 1
fi
if ! node -e 'process.exit(Number(process.versions.node.split(".")[0]) >= 18 ? 0 : 1)'; then
  echo "Se requiere Node 18 o superior." >&2
  exit 1
fi
if [ ! -d frontend/node_modules ]; then
  echo "Instalando dependencias del frontend..."
  (cd frontend && npm install --no-audit --no-fund)
fi

echo "Sembrando datos..."
DATABASE_URL="$DATABASE_URL" python -m backend.data.seed --reset

cleanup() {
  echo ""
  echo "Deteniendo servicios..."
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Backend:  http://localhost:$BACKEND_PORT/docs"
echo "Frontend: http://localhost:$FRONTEND_PORT"

DATABASE_URL="$DATABASE_URL" CORS_ORIGINS="$CORS_ORIGINS" \
  uvicorn main:app --app-dir backend --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

(
  cd frontend
  exec env VITE_API_URL="$VITE_API_URL" ./node_modules/.bin/vite --host 0.0.0.0 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

wait
