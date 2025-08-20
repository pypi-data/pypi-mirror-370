import json
import os
from pathlib import Path
from typing import Optional, Union

import appdirs
from pydantic import BaseModel


class Settings(BaseModel):
    """Settings schema for the CLI."""

    # Note: menu_page_size is currently not used due to inquirer 3.4.0 not supporting
    # the page_size parameter in List questions. This setting is kept for potential
    # future use if we switch to a different interactive library.
    menu_page_size: int = 20
    global_context_path: str = "global_context.json"
    cdc_path: str = "~/code"


def get_settings_dir() -> Path:
    """Get the settings directory for the CLI."""
    settings_dir = Path(appdirs.user_config_dir("arm-cli"))
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir


def get_settings_file() -> Path:
    """Get the path to the settings file."""
    return get_settings_dir() / "settings.json"


def load_settings() -> Settings:
    """Load settings from file, creating default if it doesn't exist."""
    settings_file = get_settings_file()

    if not settings_file.exists():
        # Create default settings
        default_settings = Settings()
        save_settings(default_settings)
        return default_settings

    try:
        with open(settings_file, "r") as f:
            data = json.load(f)
        return Settings(**data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # If settings file is corrupted, create a new one
        print(f"Warning: Settings file corrupted, creating new default settings: {e}")
        default_settings = Settings()
        save_settings(default_settings)
        return default_settings


def save_settings(settings: Settings) -> None:
    """Save settings to file."""
    settings_file = get_settings_file()

    # Ensure directory exists
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_file, "w") as f:
        json.dump(settings.model_dump(), f, indent=2)


def get_setting(key: str) -> Optional[Union[int, str, bool]]:
    """Get a specific setting value."""
    settings = load_settings()
    return getattr(settings, key, None)


def set_setting(key: str, value: Union[int, str, bool]) -> None:
    """Set a specific setting value."""
    settings = load_settings()
    if hasattr(settings, key):
        setattr(settings, key, value)
        save_settings(settings)
    else:
        raise ValueError(f"Unknown setting: {key}")
