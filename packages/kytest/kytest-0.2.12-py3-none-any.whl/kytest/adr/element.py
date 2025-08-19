import typing

from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector

from kytest.adr.driver import Driver

from kytest.utils.log import logger


# 链式调用临时存储定位方式
class ChildLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'child'


class SiblingLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'sibling'


class LeftLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'left'


class RightLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'right'


class UpLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'up'


class DownLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'down'


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
        self.locators = []

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # 链式调用方法
    def child(self, *args, **kwargs):
        self.locators.append(ChildLocator(*args, **kwargs))
        return self

    def sibling(self, *args, **kwargs):
        self.locators.append(SiblingLocator(*args, **kwargs))
        return self

    def left(self, *args, **kwargs):
        self.locators.append(LeftLocator(*args, **kwargs))
        return self

    def right(self, *args, **kwargs):
        self.locators.append(RightLocator(*args, **kwargs))
        return self

    def up(self, *args, **kwargs):
        self.locators.append(UpLocator(*args, **kwargs))
        return self

    def down(self, *args, **kwargs):
        self.locators.append(DownLocator(*args, **kwargs))
        return self

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
        logger.info(f"查找: {self._kwargs}")
        _element = self._driver.d.xpath(self._xpath) if \
            self._xpath is not None else self._driver.d(**self._kwargs)

        # 链式调用方法叠加
        if self.locators:
            logger.info(f"链式调用: {self.locators}")
            for loc_obj in self.locators:
                if loc_obj.type == "child":
                    _element = _element.child(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'sibling':
                    _element = _element.sibling(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'left':
                    _element = _element.left(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'right':
                    _element = _element.right(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'up':
                    _element = _element.up(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'down':
                    _element = _element.down(*loc_obj.args, **loc_obj.kwargs)

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
            self._driver.shot("查找失败")
            raise Exception(f"控件: {self._kwargs}, 查找失败")

    # 属性获取
    def get_text(self, timeout=5):
        logger.info("获取文本")
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
        logger.info("是否存在")
        result = False
        try:
            _element = self.find(timeout=timeout, n=0)
            result = True
        except:
            result = False
        finally:
            logger.info(result)
            return result

    def count(self, timeout=5):
        logger.info("获取定位到的控件数量")
        count = self.find(timeout=timeout).count
        logger.info(count)
        return count

    def info(self, timeout=5):
        logger.info("获取控件信息")
        info = self.find(timeout=timeout).info
        logger.info(info)
        return info

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
    def click(self, timeout=5):
        logger.info("点击")
        element = self.find(timeout=timeout)
        x, y = self._adapt_center(element)
        self._driver.util.click(x, y)
        logger.info("点击完成")

    def long_click(self, timeout=5):
        logger.info("长按")
        element = self.find(timeout=timeout)
        x, y = self._adapt_center(element)
        self._driver.long_click(x, y)
        logger.info("长按完成")

    def input(self, text, timeout=5, pwd_check=False):
        logger.info(f"输入: {text}")
        self.click(timeout=timeout)
        if pwd_check is True:
            self._driver.d(focused=True).set_text(text)
        else:
            self._driver.util.input(text)
        logger.info("输入完成")

    def clear_text(self, timeout=5, *args, **kwargs):
        logger.info("清空")
        self.find(timeout=timeout).clear_text(*args, **kwargs)
        logger.info("清空完成")

    def screenshot(self, file_path, timeout=5, full_screen=False):
        """

        @param file_path:
        @param timeout:
        @param full_screen: 为False时只截取定位到的控件，为True时截取全屏
        @return:
        """
        logger.info("截屏")
        elem = self.find(timeout=timeout)
        if full_screen is True:
            self._driver.shot(file_path)
        else:
            elem.screenshot().save(file_path)
        logger.info("截屏完成")

    def drag_to(self, timeout=5, *args, **kwargs):
        logger.info("拖动")
        self.find(timeout=timeout).drag_to(*args, **kwargs)
        logger.info("拖动完成")

    def assert_exists(self, timeout=5):
        logger.info("断言控件存在")
        try:
            assert self.exists(timeout=timeout)
        except Exception as e:
            raise e
        else:
            logger.info("断言完成")

    def assert_text_eq(self, text, timeout=5):
        logger.info(f"断言控件文本等于: {text}")
        assert text == self.get_text(timeout=timeout)
        logger.info("断言完成")

    def assert_text_ct(self, text, timeout=5):
        logger.info(f"断言控件文本包括: {text}")
        assert text in self.get_text(timeout=timeout)
        logger.info("断言完成")


if __name__ == '__main__':
    pass







