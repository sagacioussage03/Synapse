from fastapi import APIRouter
import subprocess
import psutil
import json
import time
import os

from logger import get_logger

logger = get_logger("system")
router = APIRouter(prefix="/system", tags=["System"])


# ── Termux fallback helpers ──────────────────────────────
# Android 10+ restricts /proc/* for non-root processes.
# We use shell commands as fallbacks for the stats psutil can't read.

def _termux_cpu_usage() -> dict:
    """Get CPU usage via 'top' command (works without root)."""
    try:
        result = subprocess.run(
            ["top", "-bn1", "-d0.3"],
            capture_output=True, text=True, timeout=5,
        )
        lines = result.stdout.strip().splitlines()
        # Parse %Cpu line, e.g.  "%Cpu(s):  5.3 us,  1.2 sy, ..."
        for line in lines:
            if "%Cpu" in line or "%cpu" in line.lower():
                # Extract user + sys percentages
                parts = line.split(",")
                user = 0.0
                sys_ = 0.0
                for part in parts:
                    part = part.strip()
                    if "us" in part:
                        user = float(part.split()[0])
                    elif "sy" in part:
                        sys_ = float(part.split()[0])
                return {"percent": round(user + sys_, 1), "method": "top"}
        return {}
    except Exception as e:
        logger.debug("top fallback failed: %s", e)
        return {}


def _termux_uptime() -> int:
    """Get system uptime in seconds via the 'uptime' binary or /proc/uptime."""
    # Try /proc/uptime first (sometimes allowed)
    try:
        with open("/proc/uptime", "r") as f:
            return int(float(f.readline().split()[0]))
    except (PermissionError, FileNotFoundError, Exception):
        pass

    # Fallback: parse the 'uptime' command output
    try:
        result = subprocess.run(
            ["uptime", "-s"],
            capture_output=True, text=True, timeout=3,
        )
        # uptime -s outputs: "2026-03-23 10:30:15"
        from datetime import datetime
        boot_str = result.stdout.strip()
        if boot_str:
            boot_dt = datetime.strptime(boot_str, "%Y-%m-%d %H:%M:%S")
            return int((datetime.now() - boot_dt).total_seconds())
    except Exception as e:
        logger.debug("uptime fallback failed: %s", e)

    return 0


def _termux_network_traffic() -> dict:
    """Get network traffic via /sys/class/net/ (usually accessible)."""
    net_data = {"bytes_sent": 0, "bytes_recv": 0}
    try:
        net_dir = "/sys/class/net"
        for iface in os.listdir(net_dir):
            if iface == "lo":
                continue
            rx_path = os.path.join(net_dir, iface, "statistics/rx_bytes")
            tx_path = os.path.join(net_dir, iface, "statistics/tx_bytes")
            try:
                with open(rx_path) as f:
                    net_data["bytes_recv"] += int(f.read().strip())
                with open(tx_path) as f:
                    net_data["bytes_sent"] += int(f.read().strip())
            except (PermissionError, FileNotFoundError):
                pass
        if net_data["bytes_sent"] > 0 or net_data["bytes_recv"] > 0:
            net_data["method"] = "sysfs"
            return net_data
    except Exception as e:
        logger.debug("sysfs network fallback failed: %s", e)
    return {}


# ── Routes ───────────────────────────────────────────────

@router.get("/processes")
def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    logger.info("Process scan → %d processes found", len(processes))
    return {"total": len(processes), "processes": processes}


@router.get("/health")
def get_health():
    # 1. CPU
    try:
        cpu_percent = psutil.cpu_percent(interval=0.4)
        cores = psutil.cpu_count(logical=True)
        cpu_data = {"percent": cpu_percent, "cores": cores}
    except PermissionError:
        # Fallback: use 'top' command
        fallback = _termux_cpu_usage()
        cores = psutil.cpu_count(logical=True)
        cpu_data = {
            "percent": fallback.get("percent", 0),
            "cores": cores,
        }
        if not fallback:
            logger.warning("CPU stats restricted and fallback failed")
    except Exception as e:
        logger.warning("CPU stats error: %s", e)
        cpu_data = {"percent": 0, "cores": 0, "error": str(e)}

    # 2. Memory
    try:
        mem = psutil.virtual_memory()
        mem_data = {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent,
        }
    except Exception as e:
        logger.exception("Failed to read memory stats")
        mem_data = {"error": str(e)}

    # 3. Disk (Termux Home)
    termux_home = os.environ.get("HOME", "/data/data/com.termux/files/home")
    try:
        disk = psutil.disk_usage(termux_home)
        disk_data = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
            "mount": "Termux Home",
        }
    except Exception as e:
        logger.warning("Disk stats restricted: %s", e)
        disk_data = {"error": str(e)}

    # 4. Network Traffic
    try:
        net = psutil.net_io_counters()
        net_data = {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }
    except PermissionError:
        # Fallback: read from /sys/class/net/
        net_data = _termux_network_traffic()
        if not net_data:
            logger.warning("Network counters restricted and fallback failed")
            net_data = {"error": "Android restriction"}
    except Exception as e:
        logger.warning("Network counters error: %s", e)
        net_data = {"error": str(e)}

    # 5. Uptime
    try:
        boot = psutil.boot_time()
        uptime_seconds = int(time.time() - boot)
    except (PermissionError, Exception):
        uptime_seconds = _termux_uptime()

    uptime_data = {"uptime_seconds": uptime_seconds}
    if uptime_seconds == 0:
        uptime_data["note"] = "Could not determine uptime"

    return {
        "cpu": cpu_data,
        "memory": mem_data,
        "disk": disk_data,
        "network": net_data,
        "uptime": uptime_data,
    }


@router.get("/network")
def get_network_status():
    data = {}

    try:
        wifi_proc = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, check=True,
        )
        data["wifi"] = json.loads(wifi_proc.stdout)
    except Exception as e:
        logger.warning("Wi-Fi connection info unavailable: %s", e)
        data["wifi_error"] = str(e)

    try:
        scan_proc = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True, text=True, check=True,
        )
        data["wifi_scan"] = json.loads(scan_proc.stdout)
    except Exception as e:
        logger.warning("Wi-Fi scan unavailable: %s", e)
        data["wifi_scan_error"] = str(e)

    return data


@router.get("/battery")
def get_battery_status():
    logger.info("Battery status requested")
    result = subprocess.run(
        ["termux-battery-status"],
        capture_output=True, text=True,
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        logger.warning("Could not parse battery JSON, returning raw output")
        return {"raw_output": result.stdout}