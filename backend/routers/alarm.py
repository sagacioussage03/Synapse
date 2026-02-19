from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

# Adjust this if your folder layout changes, but this matches:
# project_root/bots/alarm_bot/alarm_config.json
CONFIG_PATH = (
    Path(__file__)
    .resolve()
    .parents[2]  # .../Synapse
    / "bots"
    / "alarm_bot"
    / "alarm_config.json"
)


class AlarmConfig(BaseModel):
    time: str
    active: bool


router = APIRouter(prefix="/alarm", tags=["Alarm"])


@router.get("", response_model=AlarmConfig)
def get_alarm():
    """
    GET /alarm
    Reads bots/alarm_bot/alarm_config.json and returns it.
    If the file does not exist, returns a sensible default.
    """
    if not CONFIG_PATH.exists():
        # Default that matches your daemon's expected structure
        return AlarmConfig(time="07:00", active=False)

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return AlarmConfig(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read alarm config: {e}")


@router.post("", response_model=AlarmConfig)
def set_alarm(config: AlarmConfig):
    """
    POST /alarm
    Body: { "time": "HH:MM", "active": true/false }
    Overwrites bots/alarm_bot/alarm_config.json.
    """
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=2)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write alarm config: {e}")