from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class BaseComponent(BasePage):
    """Base class for reusable UI components that appear across multiple pages.

    Examples: header with cart badge, hamburger menu, modal dialogs.
    Components share the same Page instance as their parent page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)
