from fastapi import APIRouter
import subprocess
import json

router = APIRouter(prefix="/hardware", tags=["Hardware"])

@router.post("/torch/{state}")
def toggle_torch(state: str):
    subprocess.run(['termux-torch', state])
    return {"message": f"Flashlight is {state}"}

@router.post("/speak")
def speak(text: str):
    subprocess.run(['termux-tts-speak', text])
    return {"message": f"Synapse said: {text}"}

@router.post("/vibrate")
def vibrate(duration_ms: int = 500):
    subprocess.run(['termux-vibrate', '-f', '-d', str(duration_ms)])
    return {"message": f"Vibrated for {duration_ms}ms"}

@router.get("/battery")
def get_battery():
    result = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"raw_output": result.stdout}