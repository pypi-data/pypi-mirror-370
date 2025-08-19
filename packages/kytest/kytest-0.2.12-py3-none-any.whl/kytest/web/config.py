"""
@Author: kang.yang
@Date: 2024/10/10 11:09
"""
from typing import Literal


class BrowserConfig:
    browser_name: Literal[
                "chrome",
                "firefox",
                "webkit",
                "msedge"] = "chrome"
    headless: bool = False
    state: str = None
    maximized: bool = False
    window_size: list = None

