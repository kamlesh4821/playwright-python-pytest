from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from faker import Faker

from utils.logger import get_logger

logger = get_logger(__name__)
fake = Faker()


class TestDataProvider:
    """Loads static YAML test data and generates dynamic Faker data.

    Static data (product names, expected values) → from testdata/*.yaml
    Dynamic data (unique emails, names, addresses) → from Faker
    """

    _cache: dict[str, Any] = {}

    @classmethod
    def load(cls, filename: str) -> dict[str, Any]:
        """Load and cache a YAML test data file from the testdata/ directory."""
        if filename in cls._cache:
            return cls._cache[filename]
        path = Path("testdata") / filename
        if not path.exists():
            raise FileNotFoundError(f"Test data file not found: {path}")
        with open(path, "r") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}
        cls._cache[filename] = data
        logger.debug(f"Loaded test data: {filename}")
        return data

    @staticmethod
    def random_email() -> str:
        return fake.unique.email()

    @staticmethod
    def random_name() -> str:
        return fake.name()

    @staticmethod
    def random_first_name() -> str:
        return fake.first_name()

    @staticmethod
    def random_last_name() -> str:
        return fake.last_name()

    @staticmethod
    def random_postal_code() -> str:
        return fake.postcode()

    @staticmethod
    def random_password(length: int = 12) -> str:
        return fake.password(length=length, special_chars=True, digits=True, upper_case=True)

    @staticmethod
    def random_phone() -> str:
        return fake.phone_number()
