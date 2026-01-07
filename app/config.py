"""Compatibility wrapper for configuration.

The repo contains the implementation in top-level `app_config.py`.
This module exposes it as `app.config` to match imports used across the project.
"""

from app_config import (  # noqa: F401
    Settings,
    get_settings,
    settings,
    BASE_DIR,
    APP_DIR,
)
