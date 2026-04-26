"""
Synapse – PostgreSQL Service Handler
Manages the PostgreSQL database server via pg_ctl.
"""

import os

from logger import get_logger
from routers.services import BaseService, check_port, run_cmd, PREFIX

logger = get_logger("services.postgresql")

PG_DATA = os.path.join(PREFIX, "var", "lib", "postgresql")


class PostgreSQLService(BaseService):
    id = "postgresql"
    name = "PostgreSQL"
    icon = "🐘"
    description = "Primary relational database"
    ports = [5432]
    dependencies = []
    dependents = ["dendrite-llm"]

    def get_status(self) -> dict:
        """Check PostgreSQL status via pg_ctl."""
        rc, stdout, stderr = run_cmd(["pg_ctl", "-D", PG_DATA, "status"], timeout=5)
        running = rc == 0

        # Try to extract PID from pg_ctl status output
        # Typical output: "pg_ctl: server is running (PID: 12345)"
        pid = None
        if running:
            output = stdout + stderr
            for part in output.split():
                # Look for a number right after "PID:" or just a bare number in parens
                if part.strip("()").isdigit():
                    pid = int(part.strip("()"))
                    break

        port_open = check_port(5432)

        return {
            "running": running and port_open,
            "pid": pid,
            "port_open": port_open,
        }

    def start(self) -> dict:
        """Stop any existing instance, then start PostgreSQL."""
        # Clean stop first (ignore errors if not running)
        run_cmd(["pg_ctl", "-D", PG_DATA, "stop", "-m", "fast"], timeout=10)

        # Start
        rc, stdout, stderr = run_cmd(
            ["pg_ctl", "-D", PG_DATA, "-l", os.path.join(PG_DATA, "logfile"), "start"],
            timeout=15,
        )
        logs = (stdout + "\n" + stderr).strip()

        if rc == 0:
            return {
                "success": True,
                "message": "PostgreSQL started successfully",
                "logs": logs,
            }
        else:
            return {
                "success": False,
                "message": f"PostgreSQL failed to start (exit code {rc})",
                "logs": logs,
            }

    def stop(self) -> dict:
        """Stop PostgreSQL via pg_ctl."""
        rc, stdout, stderr = run_cmd(
            ["pg_ctl", "-D", PG_DATA, "stop", "-m", "fast"],
            timeout=10,
        )
        logs = (stdout + "\n" + stderr).strip()

        if rc == 0:
            return {
                "success": True,
                "message": "PostgreSQL stopped successfully",
                "logs": logs,
            }
        else:
            # If it wasn't running, that's still fine
            if "not running" in (stdout + stderr).lower():
                return {
                    "success": True,
                    "message": "PostgreSQL was not running",
                    "logs": logs,
                }
            return {
                "success": False,
                "message": f"PostgreSQL failed to stop (exit code {rc})",
                "logs": logs,
            }
