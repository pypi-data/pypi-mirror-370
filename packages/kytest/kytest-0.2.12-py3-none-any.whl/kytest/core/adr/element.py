import typing
from .driver import Driver

from kytest.running.conf import App
from kytest.utils.log import logger
from kytest.utils.config import FileConfig
from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector


# # 链式调用临时存储定位方式
# class ChildLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'child'
#
#
# class SiblingLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'sibling'
#
#
# class LeftLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'left'
#
#
# class RightLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'right'
#
#
# class UpLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'up'
#
#
# class DownLocator:
#
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#         self.type = 'down'


class Elem(object):
    """
    安卓控件定义
    https://github.com/openatx/uiautomator2
    """

    def __init__(self, driver: Driver = None, watch: list = None, **kwargs):
        """
        @param driver: 安卓驱动
        @param watch: 需要处理的异常弹窗定位方式列表
        """
        self._kwargs = kwargs
        self._driver = driver
        self._xpath = kwargs.get('xpath', None)
        self._watch = watch
        # self.locators = []
        if 'rid' in self._kwargs:
            self._kwargs['resourceId'] = self._kwargs.pop('rid')
        self._pkg = App.pkg
        if 'resourceId' in self._kwargs:
            if not self._kwargs['resourceId'].startswith(self._pkg):
                if not self._pkg:
                    raise KeyError('应用包名不能为空')
                else:
                    self._kwargs['resourceId'] = self._pkg + ":" + self._kwargs['resourceId']

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # # 链式调用方法
    # def child(self, *args, **kwargs):
    #     self.locators.append(ChildLocator(*args, **kwargs))
    #     return self
    #
    # def sibling(self, *args, **kwargs):
    #     self.locators.append(SiblingLocator(*args, **kwargs))
    #     return self
    #
    # def left(self, *args, **kwargs):
    #     self.locators.append(LeftLocator(*args, **kwargs))
    #     return self
    #
    # def right(self, *args, **kwargs):
    #     self.locators.append(RightLocator(*args, **kwargs))
    #     return self
    #
    # def up(self, *args, **kwargs):
    #     self.locators.append(UpLocator(*args, **kwargs))
    #     return self
    #
    # def down(self, *args, **kwargs):
    #     self.locators.append(DownLocator(*args, **kwargs))
    #     return self

    # 公共方法
    def watch_handler(self):
        """
        异常弹窗处理
        @return:
        """
        logger.info(f"开始弹窗检测: {self._watch}")
        ctx = self._driver.d.watch_context()
        for loc in self._watch:
            ctx.when(loc).click()
        ctx.wait_stable()
        ctx.close()
        logger.info("检测结束")

    def find(self, timeout=5, n=3):
        """
        增加截图的方法
        @param timeout: 每次查找时间
        @param n：失败后重试的次数
        @return:
        """
        logger.info(f"查找控件: {self._kwargs}")
        _element = self._driver.d.xpath(self._xpath) if \
            self._xpath is not None else self._driver.d(**self._kwargs)

        # # 链式调用方法叠加
        # if self.locators:
        #     logger.info(f"链式调用: {self.locators}")
        #     for loc_obj in self.locators:
        #         if loc_obj.type == "child":
        #             _element = _element.child(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'sibling':
        #             _element = _element.sibling(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'left':
        #             _element = _element.left(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'right':
        #             _element = _element.right(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'up':
        #             _element = _element.up(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'down':
        #             _element = _element.down(*loc_obj.args, **loc_obj.kwargs)

        if self._watch:
            self.watch_handler()

        retry_count = n
        if _element.wait(timeout=timeout):
            logger.info(f"查找成功")
            return _element
        else:
            if retry_count > 0:
                for count in range(1, retry_count + 1):
                    logger.info(f"第{count}次重试...")
                    if self._watch:
                        self.watch_handler()
                    if _element.wait(timeout=timeout):
                        logger.info(f"查找成功")
                        return _element

            logger.info("查找失败")
            if n > 0:
                self._driver.shot("查找失败")
            raise Exception(f"控件: {self._kwargs}, 查找失败")

    # 属性获取
    def get_text(self, timeout=5):
        logger.info(f"获取控件{self._kwargs}的文本")
        _elem = self.find(timeout=timeout)
        if isinstance(_elem, XPathSelector):
            elems = _elem.all()
        else:
            elems = list(_elem)
        text = []
        for elem in elems:
            text.append(elem.get_text())

        if len(text) == 1:
            text = text[0]

        logger.info(f"获取成功: {text}")
        return text

    def exists(self, timeout=5):
        logger.info(f"判断控件{self._kwargs}是否存在")
        result = False
        try:
            _element = self.find(timeout=timeout, n=0)
            result = True
        except:
            result = False
        finally:
            logger.info(result)
            return result

    def center(self, timeout=5, *args, **kwargs):
        return self.find(timeout=timeout).center(*args, **kwargs)

    @staticmethod
    def _adapt_center(e: typing.Union[UiObject, XPathSelector],
                      offset=(0.5, 0.5)):
        """
        修正控件中心坐标
        """
        if isinstance(e, UiObject):
            return e.center(offset=offset)
        else:
            return e.offset(offset[0], offset[1])

    # 操作
    def click_exists(self, timeout=5):
        logger.info(f"控件{self._kwargs}存在才点击")
        try:
            element = self.find(timeout=timeout, n=0)
            x, y = self._adapt_center(element)
            self._driver.click(x, y)
            logger.info("点击完成")
        except:
            logger.info("不存在，不进行操作")

    def click(self, timeout=5):
        logger.info(f"控件{self._kwargs}点击")
        element = self.find(timeout=timeout)
        x, y = self._adapt_center(element)
        self._driver.click(x, y)
        logger.info("点击完成")

    def input(self, text, timeout=5, clear=False, pwd_check=False):
        logger.info(f"控件{self._kwargs}输入: {text}")
        element = self.find(timeout=timeout)
        # 清空输入框
        if clear is True:
            element.clear_text()
        # 点击输入框
        x, y = self._adapt_center(element)
        self._driver.click(x, y)
        # 输入
        if pwd_check is True:
            self._driver.d(focused=True).set_text(text)
        else:
            self._driver.input(text)
        logger.info("输入完成")









