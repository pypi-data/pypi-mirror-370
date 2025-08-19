"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-02-18
Author: Martian Bugs
Description: 数据采集器
"""

from BrowserAutomationLauncher import BrowserInitOptions, Launcher

from ._login import Login
from .bi.bi import Bi
from .ss.ss import Ss


class Collector:
    """采集器. 使用之前请先调用 `connect_browser` 方法连接浏览器."""

    def __init__(self):
        self._launcher = Launcher()

        self._bi = None
        self._ss = None

    def connect_browser(self, port: int):
        """
        连接浏览器

        Args:
            port: 浏览器调试端口号
        """

        options = BrowserInitOptions()
        options.set_basic_options(port=port)

        self.browser = self._launcher.init_browser(options)

    def login(
        self,
        account: str,
        password: str,
    ):
        """
        聚水潭后台登录

        Args:
            account: 登录账号
            password: 登录密码
        Returns:
            如果登录成功, 将返回操作的浏览器标签页对象
        """

        login_utils = Login(browser=self.browser)
        return login_utils.login(account=account, password=password)

    @property
    def ss(self):
        """胜算模块数据采集"""

        if self._ss is None:
            self._ss = Ss(self.browser)

        return self._ss

    @property
    def bi(self):
        """报表模块数据采集"""

        if self._bi is None:
            self._bi = Bi(self.browser)

        return self._bi
