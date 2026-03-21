#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# start.sh — Launch the entire Synapse stack
# ─────────────────────────────────────────────────
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/../venv-Synapse"

# ── Activate venv (only if not already active) ──
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$VENV_DIR/bin/activate" ]; then
        echo "🔋 Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
    else
        echo "❌ Virtual environment not found at $VENV_DIR"
        echo "   Create it first:  python -m venv $VENV_DIR"
        exit 1
    fi
else
    echo "✅ Virtual environment already active ($VIRTUAL_ENV)"
fi

# ── Cleanup on Ctrl+C ──
cleanup() {
    echo ""
    echo "🛑 Shutting down Synapse..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "👋 Goodbye!"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Start Backend (FastAPI + Uvicorn) ──
echo "🚀 Starting backend on port 8000..."
cd "$PROJECT_DIR/backend"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# ── Start Frontend (Vite dev server) ──
echo "🚀 Starting frontend on port 5173..."
cd "$PROJECT_DIR/frontend"
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "─────────────────────────────────────────"
echo "  🧠 Synapse is running!"
echo "  Backend  → http://0.0.0.0:8000"
echo "  Frontend → http://0.0.0.0:5173"
echo "  Press Ctrl+C to stop everything."
echo "─────────────────────────────────────────"
echo ""

# Wait for both processes
wait
