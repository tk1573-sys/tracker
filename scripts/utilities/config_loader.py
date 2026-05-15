"""Loads YAML configuration files from the config/ directory."""
from pathlib import Path
from typing import Any, Dict
import yaml


_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def load_yaml(filename: str) -> Dict[str, Any]:
    """Load a YAML config file from the config/ directory.

    Args:
        filename: Filename (e.g. 'app_config.yaml').

    Returns:
        Parsed dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    path = _CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def get_app_config() -> Dict[str, Any]:
    """Return the parsed app_config.yaml."""
    return load_yaml("app_config.yaml")


def get_dashboard_config() -> Dict[str, Any]:
    """Return the parsed dashboard_config.yaml."""
    return load_yaml("dashboard_config.yaml")


def get_categories() -> Dict[str, Any]:
    """Return the parsed categories.yaml."""
    return load_yaml("categories.yaml")
