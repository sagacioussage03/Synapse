#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# start_bg.sh — Launch Synapse stack in background
# ─────────────────────────────────────────────────
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv-Synapse"

# Check if already running
if [ -f "$PROJECT_DIR/synapse.pid" ]; then
    echo "⚠️ Synapse may already be running. Check with ./stop.sh first."
    exit 1
fi

echo "🚀 Starting Synapse in background..."

# ── Start Backend ──
cd "$PROJECT_DIR/backend"
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Run uvicorn in background, redirect logs into the backend directory
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend/backend.log" 2>&1 &
BACKEND_PID=$!

# ── Start Frontend ──
cd "$PROJECT_DIR/frontend"
# Redirect vite logs into the frontend directory
nohup npm run dev -- --host 0.0.0.0 > "$PROJECT_DIR/frontend/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Save PIDs
cd "$PROJECT_DIR"
echo "$BACKEND_PID" > "$PROJECT_DIR/synapse.pid"
echo "$FRONTEND_PID" >> "$PROJECT_DIR/synapse.pid"

echo "✅ Synapse is running in the background!"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: backend/backend.log and frontend/frontend.log"
echo "   You can now safely close this SSH terminal."
echo "   Use ./stop.sh to stop it."
