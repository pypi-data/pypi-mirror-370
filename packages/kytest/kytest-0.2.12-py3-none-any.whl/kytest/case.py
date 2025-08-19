"""
@Author: kang.yang
@Date: 2023/10/26 09:48
"""
import time

import allure

from kytest.api.request import HttpReq
from kytest.utils.log import logger
from kytest.utils.config import kconfig


class TestCase(HttpReq):
    """
    测试用例基类，所有测试用例需要继承该类
    """
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
        project_name = kconfig['project']
        if project_name:
            allure.dynamic.feature(project_name)

        self.start()

    def teardown_method(self):
        self.end()

    # 公共方法
    @staticmethod
    def sleep(n: float):
        """休眠"""
        logger.info(f"暂停: {n}s")
        time.sleep(n)
