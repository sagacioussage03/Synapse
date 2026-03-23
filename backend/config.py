"""
Synapse – Configuration Loader
Reads config.yaml from the project root and exposes helpers.
"""

import os
import yaml

from logger import get_logger

logger = get_logger("config")

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "config.yaml")

_config: dict | None = None


def load_config(path: str = _CONFIG_PATH) -> dict:
    """Load (or reload) the YAML config file."""
    global _config
    with open(path, "r", encoding="utf-8") as f:
        _config = yaml.safe_load(f)
    logger.info("Config loaded from %s", path)
    return _config


def get_config() -> dict:
    """Return the cached config, loading it on first call."""
    if _config is None:
        load_config()
    return _config


def get_services() -> list[dict]:
    """Return the list of managed services from config."""
    cfg = get_config()
    return cfg.get("services", []) or []
