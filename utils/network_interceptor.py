from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from playwright.sync_api import Page, Route

from exceptions.network_interceptor_exception import NetworkInterceptorException
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkInterceptor:
    """Utility for intercepting and mocking Playwright network requests.

    Usage:
        interceptor = NetworkInterceptor(page)
        with interceptor.mock_response("/api/products", status=500):
            inventory_page.navigate()
            assert error_message.is_visible()
    """

    def __init__(self, page: Page) -> None:
        self._page = page

    @contextmanager
    def mock_response(
        self,
        url_pattern: str,
        status: int = 200,
        body: Optional[str] = None,
        content_type: str = "application/json",
    ) -> Generator[None, None, None]:
        """Intercept requests matching url_pattern and return a mock response."""

        def handler(route: Route) -> None:
            logger.debug(f"Intercepting {route.request.url} → status {status}")
            route.fulfill(
                status=status,
                content_type=content_type,
                body=body or "{}",
            )

        try:
            self._page.route(url_pattern, handler)
            yield
        except Exception as exc:
            raise NetworkInterceptorException(
                f"Failed to set up route intercept for '{url_pattern}': {exc}"
            ) from exc
        finally:
            try:
                self._page.unroute(url_pattern)
            except Exception:
                pass

    @contextmanager
    def abort_requests(self, url_pattern: str) -> Generator[None, None, None]:
        """Abort all requests matching url_pattern (simulates network failure)."""

        def handler(route: Route) -> None:
            logger.debug(f"Aborting request: {route.request.url}")
            route.abort()

        try:
            self._page.route(url_pattern, handler)
            yield
        finally:
            try:
                self._page.unroute(url_pattern)
            except Exception:
                pass
