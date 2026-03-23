from fastapi import APIRouter
import subprocess
import psutil
import json
import time
import os

from logger import get_logger

logger = get_logger("system")
router = APIRouter(prefix="/system", tags=["System"])


@router.get("/processes")
def get_processes():
    processes = []
    # process_iter is usually allowed in Termux for owned processes
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
    except (PermissionError, Exception) as e:
        # psutil.cpu_percent often fails on Android 10+ due to /proc/stat restrictions
        logger.warning("CPU stats restricted: %s", e)
        cpu_data = {"percent": 0, "cores": psutil.cpu_count(logical=True), "error": "Android restriction"}

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

    # 3. Disk (Pointed safely at Termux Home)
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
        logger.warning("Disk stats for %s restricted or unavailable: %s", termux_home, e)
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
    except (PermissionError, Exception) as e:
        # /proc/net/dev is often restricted on modern Android
        logger.warning("Network counters restricted: %s", e)
        net_data = {"error": "Android restriction"}

    # 5. Uptime
    uptime_seconds = 0
    try:
        boot = psutil.boot_time()
        uptime_seconds = int(time.time() - boot)
    except (PermissionError, Exception):
        # Fallback to uptime command if psutil fails
        try:
            # try reading /proc/uptime directly (sometimes allowed when psutil.boot_time is not)
            with open("/proc/uptime", "r") as f:
                uptime_seconds = int(float(f.readline().split()[0]))
        except:
            pass
            
    uptime_data = {"uptime_seconds": uptime_seconds}
    if uptime_seconds == 0:
        uptime_data["error"] = "Android restriction"

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
    # termux-api commands are usually the best way for network info on Android
    try:
        wifi_proc = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True,
            check=True,
        )
        data["wifi"] = json.loads(wifi_proc.stdout)
    except Exception as e:
        logger.warning("Wi-Fi connection info unavailable: %s", e)
        data["wifi_error"] = str(e)

    try:
        scan_proc = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True,
            text=True,
            check=True,
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
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        logger.warning("Could not parse battery JSON, returning raw output")
        return {"raw_output": result.stdout}