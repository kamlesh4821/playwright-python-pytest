from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

from exceptions.config_exception import ConfigException

load_dotenv()


class ConfigLoader:
    """Single typed access point for all framework configuration.

    Reads the YAML file matching the ENV environment variable (default: local).
    All ${VAR} placeholders in YAML are resolved from environment variables.
    Never call os.getenv() outside this class.
    """

    def __init__(self) -> None:
        env = os.getenv("ENV", "local")
        config_path = Path(__file__).parent / f"{env}.yaml"
        if not config_path.exists():
            raise ConfigException(f"Config file not found: {config_path}")
        with open(config_path, "r") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}
        self._config = self._resolve(raw)

    def _resolve(self, obj: Any) -> Any:
        """Recursively resolve ${ENV_VAR} placeholders from environment."""
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            key = obj[2:-1]
            value = os.getenv(key)
            if value is None:
                raise ConfigException(f"Required environment variable '{key}' is not set.")
            return value
        if isinstance(obj, dict):
            return {k: self._resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._resolve(i) for i in obj]
        return obj

    def get_base_url(self) -> str:
        return str(self._config["base_url"])

    def get_browser(self) -> str:
        return str(os.getenv("BROWSER", self._config.get("browser", "chromium")))

    def is_headless(self) -> bool:
        env_val = os.getenv("HEADLESS")
        if env_val is not None:
            return env_val.lower() == "true"
        return bool(self._config.get("headless", True))

    def get_action_timeout(self) -> int:
        return int(self._config.get("action_timeout_ms", 10000))

    def get_navigation_timeout(self) -> int:
        return int(self._config.get("navigation_timeout_ms", 30000))

    def get_screenshot_on_failure(self) -> bool:
        return bool(self._config.get("screenshot_on_failure", True))

    def get_video_on_failure(self) -> bool:
        env_val = os.getenv("VIDEO")
        if env_val is not None:
            return env_val.lower() == "true"
        return bool(self._config.get("video_on_failure", False))

    def get_browser_args(self) -> list[str]:
        return list(self._config.get("browser_args", []))

    def get_db_config(self) -> dict[str, Any]:
        return dict(self._config.get("database", {}))

    def get_db_url(self) -> str:
        db = self.get_db_config()
        if not db:
            raise ConfigException("Database configuration is missing from config file.")
        return (
            f"postgresql://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['name']}"
        )

    def get_test_username(self) -> str:
        value = os.getenv("TEST_USERNAME", "standard_user")
        return str(value)

    def get_test_password(self) -> str:
        value = os.getenv("TEST_PASSWORD", "secret_sauce")
        return str(value)

    def get_parallel_workers(self) -> int:
        return int(os.getenv("PARALLEL_WORKERS", "4"))

    def get_retry_count(self) -> int:
        return int(os.getenv("RETRY_COUNT", "1"))
