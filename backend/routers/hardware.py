from fastapi import APIRouter
import subprocess
import json

from logger import get_logger

logger = get_logger("hardware")
router = APIRouter(prefix="/hardware", tags=["Hardware"])


@router.post("/torch/{state}")
def toggle_torch(state: str):
    logger.info("Torch toggled → %s", state)
    subprocess.run(['termux-torch', state])
    return {"message": f"Flashlight is {state}"}


@router.post("/speak")
def speak(text: str):
    logger.info("TTS request: %s", text[:80])
    subprocess.run(['termux-tts-speak', text])
    return {"message": f"Synapse said: {text}"}


@router.post("/vibrate")
def vibrate(duration_ms: int = 500):
    logger.info("Vibrate → %d ms", duration_ms)
    subprocess.run(['termux-vibrate', '-f', '-d', str(duration_ms)])
    return {"message": f"Vibrated for {duration_ms}ms"}