from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import allure
from playwright.sync_api import Page

from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotUtil:
    """Handles screenshot capture and Allure attachment."""

    SCREENSHOTS_DIR = Path("reports/screenshots")

    @classmethod
    def capture_on_failure(cls, page: Page, test_name: str) -> Optional[Path]:
        """Capture a full-page screenshot and attach it to the Allure report."""
        try:
            cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = test_name.replace("/", "_").replace(" ", "_")
            path = cls.SCREENSHOTS_DIR / f"{safe_name}_{timestamp}.png"
            page.screenshot(path=str(path), full_page=True)
            with open(path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"Screenshot — {test_name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            logger.debug(f"Screenshot saved: {path}")
            return path
        except Exception as exc:
            logger.error(f"Screenshot capture failed: {exc}")
            return None

    @classmethod
    def capture_trace_on_failure(cls, context: object, test_name: str) -> None:
        """Stop Playwright tracing and save the trace zip file."""
        try:
            traces_dir = Path("reports/traces")
            traces_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = test_name.replace("/", "_").replace(" ", "_")
            trace_path = traces_dir / f"{safe_name}_{timestamp}.zip"
            context.tracing.stop(path=str(trace_path))  # type: ignore[attr-defined]
            allure.attach.file(
                str(trace_path),
                name=f"Trace — {test_name}",
                attachment_type=allure.attachment_type.ZIP,
            )
        except Exception as exc:
            logger.error(f"Trace capture failed: {exc}")
