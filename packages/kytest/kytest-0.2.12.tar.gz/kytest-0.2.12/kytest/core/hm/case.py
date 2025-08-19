"""
@Author: kang.yang
@Date: 2023/10/26 09:48
"""
import time

from .driver import HmDriver
from .element import Elem

from kytest.utils.log import logger
from kytest.core.api.request import HttpReq
from kytest.running.conf import App


class TestCase(HttpReq):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    dr: HmDriver = None

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
        try:
            cls().start_class()
        except BaseException as e:
            logger.error(f"start_class Exception: {e}")

    @classmethod
    def teardown_class(cls):
        try:
            cls().end_class()
        except BaseException as e:
            logger.error(f"end_class Exception: {e}")

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
        # 驱动初始化
        self.dr = HmDriver(App.did)
        # 设备解锁
        self.dr.unlock()
        self.start()

    def teardown_method(self):
        self.end()

    # 公共方法
    @staticmethod
    def sleep(n: float):
        """休眠"""
        logger.info(f"暂停: {n}s")
        time.sleep(n)

    def shot(self, name: str, delay=0):
        """截图"""
        if delay:
            self.sleep(delay)
        self.dr.shot(name)

    # UI方法
    def elem(self, **kwargs):
        """
        元素定位方法
        @return:
        """
        return Elem(driver=self.dr, **kwargs)

    def start_app(self, force=True):
        """
        启动应用
        @return:
        """
        if App.ability is None:
            raise KeyError('ability不能为空')
        if force is True:
            self.stop_app()
        self.dr.start_app(App.pkg, App.ability)

    def stop_app(self):
        """
        停止应用
        @return:
        """
        self.dr.stop_app(App.pkg)

