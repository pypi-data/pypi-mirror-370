"""Environment configuration and .env file loading for OHDSI WebAPI client."""

import os
from pathlib import Path
from typing import Optional


def load_env(env_file: Optional[str] = None) -> None:
    """Load environment variables from .env file.

    This function automatically looks for .env files in the following order:
    1. Explicit env_file path (if provided)
    2. .env in current working directory
    3. .env in project root (where pyproject.toml is located)

    Args:
        env_file: Optional explicit path to .env file
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        # python-dotenv not installed, skip loading
        return

    # If explicit file provided, try to load it
    if env_file:
        if Path(env_file).exists():
            load_dotenv(env_file)
            return
        else:
            raise FileNotFoundError(f"Environment file not found: {env_file}")

    # Auto-discover .env files
    env_paths = [
        Path.cwd() / ".env",  # Current working directory
    ]

    # Find project root (where pyproject.toml is)
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            env_paths.append(current / ".env")
            break
        current = current.parent

    # Load the first .env file found
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable with proper parsing."""
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    else:
        return default


def get_env_int(key: str, default: int) -> int:
    """Get integer environment variable with fallback."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_float(key: str, default: float) -> float:
    """Get float environment variable with fallback."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


# Auto-load .env on import (convenient for development)
load_env()
