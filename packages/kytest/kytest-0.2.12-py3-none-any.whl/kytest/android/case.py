"""
@Author: kang.yang
@Date: 2023/10/26 09:48
"""
import time

import allure

from .driver import AdrDriver
from .element import AdrElem
from kytest.utils.log import logger
from kytest.utils.config import KyConfig
from kytest.api.request import HttpReq
from kytest.running.conf import App


class TestCase(HttpReq):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    driver: AdrDriver = None

    # ---------------------初始化-------------------------------
    def start_class(self):
        """
        Hook method for setup_class fixture
        :return:
        """
        pass

    def end_class(self):
        """
        Hook method for teardown_class fixture
        :return:
        """
        pass

    @classmethod
    def setup_class(cls):
        cls().start_class()

    @classmethod
    def teardown_class(cls):
        cls().end_class()

    def start(self):
        """
        Hook method for setup_method fixture
        :return:
        """
        pass

    def end(self):
        """
        Hook method for teardown_method fixture
        :return:
        """
        pass

    def setup_method(self):
        project_name = KyConfig.get_common('project')
        if project_name:
            allure.dynamic.feature(project_name)
        self.start_time = time.time()

        # device_id = config.get_app("serial")
        # pkg_name = config.get_app("package")
        self.driver = AdrDriver(App.serial, App.package)
        if App.auto_start is True:
            self.driver.start_app()

        self.start()

    def teardown_method(self):
        self.end()

        if App.auto_start is True:
            self.driver.stop_app()

        take_time = time.time() - self.start_time
        logger.info("用例耗时: {:.2f} s".format(take_time))

    # 公共方法
    @staticmethod
    def sleep(n: float):
        """休眠"""
        logger.info(f"暂停: {n}s")
        time.sleep(n)

    def screenshot(self, name: str):
        """截图"""
        self.driver.screenshot(name)

    # UI方法
    def elem(self, *args, **kwargs):
        return AdrElem(self.driver, *args, **kwargs)

    # 安卓方法
    def assert_act(self, activity_name: str, timeout=5):
        """断言当前页面的activity"""
        self.driver.assert_act(activity_name, timeout)
