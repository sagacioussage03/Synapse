"""
Synapse – Ollama Service Handler
Manages the Ollama LLM server process.
"""

import os
import time
import subprocess

from logger import get_logger
from routers.services import BaseService, check_port, run_cmd, tail_file, HOME

logger = get_logger("services.ollama")

OLLAMA_LOG = os.path.join(HOME, "projects", "ollama-logs", "ollama.log")


class OllamaService(BaseService):
    id = "ollama"
    name = "Ollama"
    icon = "🦙"
    description = "Local LLM server"
    ports = [11434]
    dependencies = []
    dependents = ["dendrite-llm"]

    def get_status(self) -> dict:
        """Check if Ollama is running via pgrep + port check."""
        rc, stdout, _ = run_cmd(["pgrep", "-x", "ollama"], timeout=3)
        pid = None
        if rc == 0 and stdout.strip():
            # pgrep returns one PID per line; take the first
            try:
                pid = int(stdout.strip().splitlines()[0])
            except (ValueError, IndexError):
                pass

        port_open = check_port(11434)

        return {
            "running": pid is not None or port_open,
            "pid": pid,
            "port_open": port_open,
        }

    def start(self) -> dict:
        """Kill existing Ollama, clear logs, then start fresh."""
        # Clean kill first
        run_cmd(["pkill", "-x", "ollama"], timeout=5)
        time.sleep(1)

        # Ensure log directory exists
        log_dir = os.path.dirname(OLLAMA_LOG)
        os.makedirs(log_dir, exist_ok=True)

        # Clear old logs for a fresh start
        try:
            with open(OLLAMA_LOG, "w") as f:
                f.truncate(0)
        except Exception:
            pass

        # Start Ollama in background with OLLAMA_HOST=0.0.0.0
        try:
            env = {**os.environ, "OLLAMA_HOST": "0.0.0.0"}
            with open(OLLAMA_LOG, "w") as log_f:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=log_f,
                    stderr=log_f,
                    env=env,
                    start_new_session=True,
                )
        except FileNotFoundError:
            return {
                "success": False,
                "message": "Ollama binary not found. Is it installed?",
                "logs": "",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start Ollama: {e}",
                "logs": "",
            }

        # Wait for it to come up
        time.sleep(3)

        # Read logs and verify
        logs = tail_file(OLLAMA_LOG, lines=30)
        status = self.get_status()

        if status["running"]:
            return {
                "success": True,
                "message": "Ollama started successfully",
                "logs": logs,
            }
        else:
            return {
                "success": False,
                "message": "Ollama process started but is not responding on port 11434",
                "logs": logs,
            }

    def stop(self) -> dict:
        """Stop Ollama by killing the process."""
        rc, stdout, stderr = run_cmd(["pkill", "-x", "ollama"], timeout=5)
        time.sleep(1)

        logs = (stdout + "\n" + stderr).strip()
        status = self.get_status()

        if not status["running"]:
            return {
                "success": True,
                "message": "Ollama stopped successfully",
                "logs": logs if logs else "Process terminated",
            }
        else:
            # Force kill
            run_cmd(["pkill", "-9", "-x", "ollama"], timeout=5)
            time.sleep(0.5)
            return {
                "success": True,
                "message": "Ollama force-killed",
                "logs": logs if logs else "Process force-terminated",
            }
