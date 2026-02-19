from fastapi import APIRouter
import subprocess
import psutil
import json
import time
import os

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/processes")
def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            processes.append(proc.info)
        except psutil.NoSuchProcess:
            pass
    return {"total": len(processes), "processes": processes}

@router.get("/pm2")
def get_pm2_status():
    try:
        result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True)
        return {"pm2_apps": json.loads(result.stdout)}
    except Exception as e:
         return {"error": "PM2 might not be in PATH", "details": str(e)}

@router.get("/health")
def get_health():
    cpu_percent = psutil.cpu_percent(interval=0.4)
    mem = psutil.virtual_memory()
    
    # 🟢 Point to Termux's home folder, NOT the root "/"
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
        disk_data = {"error": str(e)}

    net = psutil.net_io_counters()

    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "available": mem.available,
            "percent": mem.percent,
        },
        "disk": disk_data,
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        },
        "uptime": {
            "boot_time": psutil.boot_time(),
            "uptime_seconds": int(time.time() - psutil.boot_time()),
        },
    }

@router.get("/network")
def get_network_status():
    data = {}

    # Termux Wi-Fi connection info
    try:
        wifi_proc = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True,
            check=True,
        )
        data["wifi"] = json.loads(wifi_proc.stdout)
    except Exception as e:
        data["wifi_error"] = str(e)

    # Optionally, simple IP info via termux or ip route / ifconfig etc.
    # Example: termux-wifi-scaninfo returns array of networks
    try:
        scan_proc = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True,
            text=True,
            check=True,
        )
        data["wifi_scan"] = json.loads(scan_proc.stdout)
    except Exception as e:
        data["wifi_scan_error"] = str(e)

    return data

@router.get("/battery")
def get_battery_status():
    result = subprocess.run(
        ["termux-battery-status"],
        capture_output=True,
        text=True,
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"raw_output": result.stdout}