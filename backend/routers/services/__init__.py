"""
Synapse – Service Management Router
Base class, shared helpers, service registry, and FastAPI endpoints.
Each service is defined in its own module for modularity.
"""

import socket
import subprocess
import os
from abc import ABC, abstractmethod
from collections import OrderedDict

from fastapi import APIRouter, HTTPException

from logger import get_logger

logger = get_logger("services")

router = APIRouter(prefix="/services", tags=["Services"])


# ── Shared helpers ───────────────────────────────────────

HOME = os.path.expanduser("~")
PREFIX = os.environ.get("PREFIX", "/data/data/com.termux/files/usr")


def check_port(port: int, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    """Return True if a TCP connection to host:port succeeds."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def tail_file(path: str, lines: int = 30) -> str:
    """Read the last N lines of a file, returning '' if the file doesn't exist."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except (FileNotFoundError, PermissionError):
        return ""


def run_cmd(
    args: list[str],
    timeout: int = 15,
    env: dict | None = None,
) -> tuple[int, str, str]:
    """
    Run a command synchronously and return (returncode, stdout, stderr).
    Merges the given env dict with the current environment.
    """
    merged_env = {**os.environ, **(env or {})}
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=merged_env,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {args[0]}"
    except Exception as e:
        return -1, "", str(e)


# ── Base class ───────────────────────────────────────────

class BaseService(ABC):
    """Abstract base for every managed service."""

    id: str
    name: str
    icon: str
    description: str
    ports: list[int]
    dependencies: list[str] = []
    dependents: list[str] = []

    @abstractmethod
    def get_status(self) -> dict:
        """Check if the service is running. Must return at minimum: {running, pid}."""
        ...

    @abstractmethod
    def start(self) -> dict:
        """Start the service (clean start). Returns {success, message, logs}."""
        ...

    @abstractmethod
    def stop(self) -> dict:
        """Stop the service. Returns {success, message, logs}."""
        ...

    def to_status_dict(self) -> dict:
        """Build the full status payload for this service."""
        status = self.get_status()
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "description": self.description,
            "ports": self.ports,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            **status,
        }


# ── Service registry ────────────────────────────────────
# Populated at import time by each service module.

SERVICES: OrderedDict[str, BaseService] = OrderedDict()


def register(service: BaseService) -> None:
    """Add a service to the global registry."""
    SERVICES[service.id] = service


# Import service modules to trigger registration
from routers.services.postgresql import PostgreSQLService      # noqa: E402
from routers.services.ollama import OllamaService              # noqa: E402
from routers.services.dendrite_llm import DendriteLLMService   # noqa: E402

register(PostgreSQLService())
register(OllamaService())
register(DendriteLLMService())


# ── Routes ───────────────────────────────────────────────

@router.get("/status")
def get_all_status():
    """Return the status of every registered service."""
    services = []
    for svc in SERVICES.values():
        try:
            status = svc.to_status_dict()
            # Enrich with dependency-met info
            if svc.dependencies:
                missing = []
                for dep_id in svc.dependencies:
                    dep = SERVICES.get(dep_id)
                    if dep and not dep.get_status().get("running"):
                        missing.append(dep_id)
                status["dependencies_met"] = len(missing) == 0
                status["missing_dependencies"] = missing
            else:
                status["dependencies_met"] = True
                status["missing_dependencies"] = []
            services.append(status)
        except Exception as e:
            logger.error("Status check failed for %s: %s", svc.id, e)
            services.append({
                "id": svc.id,
                "name": svc.name,
                "icon": svc.icon,
                "description": svc.description,
                "ports": svc.ports,
                "running": False,
                "pid": None,
                "error": str(e),
                "dependencies_met": False,
                "missing_dependencies": svc.dependencies,
            })
    return {"services": services}


@router.post("/{service_id}/start")
def start_service(service_id: str):
    """Start a service. Validates dependencies first."""
    svc = SERVICES.get(service_id)
    if not svc:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service_id}")

    # Dependency check
    if svc.dependencies:
        missing = []
        for dep_id in svc.dependencies:
            dep = SERVICES.get(dep_id)
            if dep and not dep.get_status().get("running"):
                missing.append(SERVICES[dep_id].name)
        if missing:
            missing_str = ", ".join(missing)
            logger.warning(
                "Cannot start %s: missing dependencies: %s", svc.name, missing_str
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "service_id": service_id,
                    "action": "start",
                    "success": False,
                    "message": f"Cannot start {svc.name}: requires {missing_str} to be running first",
                    "missing_dependencies": missing,
                },
            )

    logger.info("Starting service: %s", svc.name)
    result = svc.start()
    result["service_id"] = service_id
    result["action"] = "start"
    result["dependencies_met"] = True

    if result.get("success"):
        logger.info("Service %s started successfully", svc.name)
    else:
        logger.error("Service %s failed to start: %s", svc.name, result.get("message"))

    return result


@router.post("/{service_id}/stop")
def stop_service(service_id: str):
    """Stop a service."""
    svc = SERVICES.get(service_id)
    if not svc:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service_id}")

    logger.info("Stopping service: %s", svc.name)
    result = svc.stop()
    result["service_id"] = service_id
    result["action"] = "stop"

    if result.get("success"):
        logger.info("Service %s stopped successfully", svc.name)
    else:
        logger.error("Service %s failed to stop: %s", svc.name, result.get("message"))

    return result
