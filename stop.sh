#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# stop.sh — Stop Synapse stack
# ─────────────────────────────────────────────────
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/synapse.pid"

if [ -f "$PID_FILE" ]; then
    echo "🛑 Stopping Synapse..."
    
    # Read PIDs
    BACKEND_PID=$(sed -n '1p' "$PID_FILE")
    FRONTEND_PID=$(sed -n '2p' "$PID_FILE")
    
    # Kill processes gracefully if they exist
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   Killing Backend ($BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   Killing Frontend ($FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Child processes of Vite might linger, so pkill as a fallback
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    # Clean up
    rm "$PID_FILE"
    echo "👋 Synapse stopped."
else
    echo "⚠️ No synapse.pid found. Attempting to kill by process name..."
    pkill -f "uvicorn main:app" && echo "   Backend stopped." || echo "   Backend not found."
    pkill -f "vite" && echo "   Frontend stopped." || echo "   Frontend not found."
    echo "👋 Synapse stopped."
fi
