"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-18
Author: Martian Bugs
Description: 胜算模块数据采集
"""

from BrowserAutomationLauncher import Browser

from .report import Report


class Ss:
    def __init__(self, browser: Browser):
        self._browser = browser

        self._report = None

    @property
    def report(self):
        """报表模块数据采集"""

        if self._report is None:
            self._report = Report(self._browser)

        return self._report
