"""
Synapse – Dendrite-LLM Service Handler
Manages the Dendrite-LLM full-stack application via its start.sh / stop.sh scripts.
"""

import os
import time

from logger import get_logger
from routers.services import BaseService, check_port, run_cmd, tail_file, HOME

logger = get_logger("services.dendrite_llm")

DENDRITE_DIR = os.path.join(HOME, "projects", "Dendrite-LLM")
PID_DIR = os.path.join(DENDRITE_DIR, ".pids")
START_SCRIPT = os.path.join(DENDRITE_DIR, "start.sh")
STOP_SCRIPT = os.path.join(DENDRITE_DIR, "stop.sh")
BACKEND_LOG = os.path.join(PID_DIR, "backend.log")
FRONTEND_LOG = os.path.join(PID_DIR, "frontend.log")
BACKEND_PID_FILE = os.path.join(PID_DIR, "backend.pid")
FRONTEND_PID_FILE = os.path.join(PID_DIR, "frontend.pid")


def _read_pid(pid_file: str) -> int | None:
    """Read a PID from a file, returning None if unreadable."""
    try:
        with open(pid_file, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError, PermissionError):
        return None


def _pid_alive(pid: int | None) -> bool:
    """Check if a PID is still alive."""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


class DendriteLLMService(BaseService):
    id = "dendrite-llm"
    name = "Dendrite-LLM"
    icon = "🌿"
    description = "Self-hosted LLM chat application"
    ports = [8001, 3000]
    dependencies = ["postgresql", "ollama"]
    dependents = []

    def get_status(self) -> dict:
        """Check Dendrite-LLM status via PID files + port reachability."""
        backend_pid = _read_pid(BACKEND_PID_FILE)
        frontend_pid = _read_pid(FRONTEND_PID_FILE)

        backend_alive = _pid_alive(backend_pid)
        frontend_alive = _pid_alive(frontend_pid)

        backend_port = check_port(8001)
        frontend_port = check_port(3000)

        # Consider "running" if at least the backend is up
        running = (backend_alive or backend_port) and (frontend_alive or frontend_port)

        return {
            "running": running,
            "pid": backend_pid if backend_alive else frontend_pid if frontend_alive else None,
            "backend": {
                "pid": backend_pid,
                "alive": backend_alive,
                "port_open": backend_port,
            },
            "frontend": {
                "pid": frontend_pid,
                "alive": frontend_alive,
                "port_open": frontend_port,
            },
        }

    def start(self) -> dict:
        """Stop any existing instance, then start via start.sh."""
        # Clean stop first
        if os.path.isfile(STOP_SCRIPT):
            run_cmd(["bash", STOP_SCRIPT], timeout=15)
            time.sleep(1)

        # Verify the start script exists
        if not os.path.isfile(START_SCRIPT):
            return {
                "success": False,
                "message": f"Start script not found: {START_SCRIPT}",
                "logs": "",
            }

        # Run start.sh
        rc, stdout, stderr = run_cmd(
            ["bash", START_SCRIPT],
            timeout=30,
        )
        combined = (stdout + "\n" + stderr).strip()

        # Wait for services to come up
        time.sleep(3)

        # Read service-specific logs
        backend_logs = tail_file(BACKEND_LOG, lines=20)
        frontend_logs = tail_file(FRONTEND_LOG, lines=20)

        logs_parts = [combined]
        if backend_logs:
            logs_parts.append(f"\n── Backend Log ──\n{backend_logs}")
        if frontend_logs:
            logs_parts.append(f"\n── Frontend Log ──\n{frontend_logs}")
        logs = "\n".join(logs_parts)

        # Verify status
        status = self.get_status()

        if status["running"]:
            return {
                "success": True,
                "message": "Dendrite-LLM started successfully",
                "logs": logs,
            }
        else:
            return {
                "success": False,
                "message": "Dendrite-LLM start script ran but services are not responding",
                "logs": logs,
            }

    def stop(self) -> dict:
        """Stop Dendrite-LLM via stop.sh."""
        if not os.path.isfile(STOP_SCRIPT):
            return {
                "success": False,
                "message": f"Stop script not found: {STOP_SCRIPT}",
                "logs": "",
            }

        rc, stdout, stderr = run_cmd(
            ["bash", STOP_SCRIPT],
            timeout=15,
        )
        logs = (stdout + "\n" + stderr).strip()

        time.sleep(1)
        status = self.get_status()

        if not status["running"]:
            return {
                "success": True,
                "message": "Dendrite-LLM stopped successfully",
                "logs": logs,
            }
        else:
            return {
                "success": False,
                "message": "Stop script ran but services are still running",
                "logs": logs,
            }
