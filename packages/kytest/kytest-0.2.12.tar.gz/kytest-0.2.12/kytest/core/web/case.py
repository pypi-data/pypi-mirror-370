"""
@Author: kang.yang
@Date: 2023/10/26 09:48
"""
import time

from .driver import Driver
from .element import Elem

from urllib import parse
from kytest.core.api.request import HttpReq
from kytest.utils.log import logger
from kytest.utils.config import FileConfig


class TestCase(HttpReq):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    dr: Driver = None

    # ---------------------初始化-------------------------------
    @classmethod
    def start_class(cls):
        """
        Hook method for setup_class fixture
        :return:
        """
        pass

    @classmethod
    def end_class(cls):
        """
        Hook method for teardown_class fixture
        :return:
        """
        pass

    @classmethod
    def setup_class(cls):
        cls.dr = Driver(
            browserName=FileConfig.get_web('browser'),
            headless=FileConfig.get_web('headless'),
            state=FileConfig.get_web('state'),
            maximized=FileConfig.get_web('maximized'),
            window_size=FileConfig.get_web('window_size')
        )  # 各种配置参数后面再加吧
        cls.context = cls.dr.context
        cls.page = cls.dr.page

        cls.start_class()

    @classmethod
    def teardown_class(cls):
        cls.end_class()
        cls.dr.close()

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
        return Elem(self.dr, **kwargs)

    @staticmethod
    def is_url_has_http(url):
        """针对为空和只有路径的情况，使用默认host进行补全"""
        host = FileConfig.get_web('web_url')
        if url is None:
            url = host
        if 'http' not in url:
            url = parse.urljoin(host, url)
        return url

    def goto(self, url):
        """打开页面"""
        url = self.is_url_has_http(url)
        self.dr.goto(url)


