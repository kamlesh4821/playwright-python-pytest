from __future__ import annotations
from typing import Optional


class FrameworkException(Exception):
    """Base exception for all framework-level errors."""

    def __init__(
        self,
        message: str,
        test_name: Optional[str] = None,
        browser: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        self.test_name = test_name
        self.browser = browser
        self.url = url
        context = " | ".join(
            f"{k}={v}"
            for k, v in {"test": test_name, "browser": browser, "url": url}.items()
            if v
        )
        full_message = f"{message} [{context}]" if context else message
        super().__init__(full_message)
