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
    
    # Kill any existing TTS tasks to avoid overlapping/hanging
    subprocess.run(['pkill', '-f', 'termux-tts-speak'], capture_output=True)
    subprocess.run(['pkill', '-f', 'TextToSpeech'], capture_output=True)
    
    try:
        # 30-second timeout to ensure the process never permanently hangs the thread
        subprocess.run(['termux-tts-speak', text], timeout=30)
        return {"message": f"Synapse said: {text}"}
    except subprocess.TimeoutExpired:
        logger.error("TTS request timed out after 30 seconds")
        subprocess.run(['pkill', '-f', 'termux-tts-speak'], capture_output=True)
        return {"error": "TTS request timed out"}


@router.post("/vibrate")
def vibrate(duration_ms: int = 500):
    logger.info("Vibrate → %d ms", duration_ms)
    subprocess.run(['termux-vibrate', '-f', '-d', str(duration_ms)])
    return {"message": f"Vibrated for {duration_ms}ms"}