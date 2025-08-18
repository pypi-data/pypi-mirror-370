"""OHDSI WebAPI Python Client."""

# Load environment variables from .env file (if present)
from .client import WebApiClient
from .env import load_env

load_env()

__all__ = ["WebApiClient"]
