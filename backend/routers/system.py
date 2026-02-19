from fastapi import APIRouter
import subprocess
import psutil
import json

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