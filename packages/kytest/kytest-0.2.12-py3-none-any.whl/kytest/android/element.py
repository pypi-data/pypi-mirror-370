import typing

from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector

from .driver import AdrDriver
from kytest.utils.exceptions import KError
from kytest.utils.log import logger
# from kytest.utils.common import calculate_time, \
#     draw_red_by_coordinate
# from image.element import ImgElem
# from ocr import OcrElem


class AdrElem(object):
    """
    安卓元素定义
    """

    def __init__(self,
                 driver: AdrDriver = None,
                 rid: str = None,
                 className: str = None,
                 text: str = None,
                 textCont: str = None,
                 xpath: str = None,
                 # image: str = None,
                 # ocr: str = None,
                 region: int = None,
                 # grade: float = 0.8,
                 index: int = None,):
                 # _debug: bool = False):
        """

        @param driver: 安卓驱动
        @param rid: resourceId定位
        @param className: className定位
        @param text: 文本定位
        @param textCont: 文本模糊匹配
        @param xpath: xpath定位
        @param region: ocr识别区域设置，支持1、2、3、4
        @param index: 识别到多个元素时，根据index获取其中一个
        """
        self._kwargs = {}
        if rid is not None:
            self._kwargs["resourceId"] = rid
        if className is not None:
            self._kwargs["className"] = className
        if text is not None:
            self._kwargs["text"] = text
        if textCont is not None:
            self._kwargs["textContains"] = textCont
        if xpath:
            self._kwargs["xpath"] = xpath
        if index is not None:
            self._kwargs["instance"] = index

        self._driver = driver
        self._xpath = xpath
        # self._debug = _debug
        # self._image = image
        # self._ocr = ocr
        self._pos = region
        # self._grade = grade

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    def find(self, timeout=10, watch=None):
        """
        增加截图的方法
        @param timeout: 每次查找时间
        @param watch: 增加弹窗检测，定位方式列表，用text定位
        watch为True时，使用内置库
            when("继续使用")
            when("移入管控").when("取消")
            when("^立即(下载|更新)").when("取消")
            when("同意")
            when("^(好的|确定)")
            when("继续安装")
            when("安装")
            when("Agree")
            when("ALLOW")
        watch为list时，使用内置库+watch
        @return:
        """
        rid = self._kwargs.get("resourceId", None)
        if rid is not None:
            pkg_name = self._driver.pkg_name
            if pkg_name is None:
                pkg_name: str = self._driver.d.app_current()['package']
                if pkg_name.endswith("launcher"):
                    raise KError('包名不能为空')
            if not pkg_name.startswith("com."):
                if "id/" not in rid:
                    self._kwargs["resourceId"] = pkg_name + ":id/" + rid
                else:
                    self._kwargs["resourceId"] = pkg_name + ":" + rid

        def _find():
            _element = self._driver.d.xpath(self._xpath) if \
                self._xpath is not None else self._driver.d(**self._kwargs)

            if _element.wait(timeout=timeout):
                logger.info(f"查找成功")
                # if self._debug is True:
                #     file_path = self._driver.screenshot("查找成功")
                #     logger.debug(file_path)
                #     draw_red_by_coordinate(file_path, _element.bounds())
                return _element
            else:
                logger.info(f"查找失败")
                self._driver.screenshot("查找失败")
                raise KError(f"控件: {self._kwargs}, 查找失败")

        if watch:
            logger.info("开启弹窗检测")
            if isinstance(watch, list):
                with self._driver.d.watch_context(builtin=True) as ctx:
                    for text in watch:
                        ctx.when(text).click()
                    ctx.wait_stable()
                    logger.info("结束检测")
                    return _find()
            else:
                with self._driver.d.watch_context(builtin=True) as ctx:
                    ctx.wait_stable()
                    logger.info("结束检测")
                    return _find()
        else:
            return _find()

    def text(self):
        logger.info(f"获取文本属性")
        _elem = self.find(timeout=3)
        if isinstance(_elem, XPathSelector):
            elems = _elem.all()
        else:
            elems = list(_elem)
        text = []
        for elem in elems:
            text.append(elem.get_text())

        if len(text) == 1:
            text = text[0]
        logger.info(text)
        return text

    def exists(self, timeout=5):
        logger.info(f"检查控件是否存在")
        # if self._image is not None:
        #     return ImgElem(self._driver,
        #                    file=self._image,
        #                    grade=self._grade,
        #                    _debug=self._debug).exists(timeout=timeout)
        # elif self._ocr is not None:
        #     return OcrElem(self._driver,
        #                    text=self._ocr,
        #                    pos=self._pos,
        #                    grade=self._grade,
        #                    _debug=self._debug).exists(timeout=timeout)
        # else:

        result = False
        try:
            _element = self.find(timeout=timeout)
            result = True
        except Exception as e:
            logger.debug(str(e))
            result = False
        finally:
            logger.info(result)
            return result

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

    def click(self, timeout=5, watch=None):
        logger.info(f"点击 {self._kwargs}")
        # if self._image is not None:
        #     return ImgElem(self._driver,
        #                    file=self._image,
        #                    grade=self._grade,
        #                    _debug=self._debug).click(timeout=timeout)
        # elif self._ocr is not None:
        #     return OcrElem(self._driver,
        #                    text=self._ocr,
        #                    pos=self._pos,
        #                    grade=self._grade,
        #                    _debug=self._debug).click(timeout=timeout)
        # else:

        element = self.find(timeout=timeout, watch=watch)
        # 这种方式经常点击不成功，感觉是页面刷新有影响
        # element.click()
        x, y = self._adapt_center(element)
        self._driver.d.click(x, y)
        logger.info("点击完成")

    def click_exists(self, timeout=5, watch=None):
        logger.info(f"{self._kwargs} 存在才点击")
        if self.exists(timeout=timeout):
            self.click(watch=watch)
        else:
            logger.info("控件不存在")

    def input(self, text, watch=None, enter=False):
        logger.info(f"输入文本: {text}")
        self.find(watch=watch).set_text(text)
        if enter is True:
            self._driver.enter()
        logger.info("输入完成")

    def input_exists(self, text: str, timeout=5, watch=None, enter=False):
        logger.info(f"{self._kwargs} 存在才输入: {text}")
        if self.exists(timeout=timeout):
            self.input(text, watch=watch, enter=enter)
        else:
            logger.info("输入框不存在")

    def input_pwd(self, text, watch=None, enter=False):
        """密码输入框输入有时候用input输入不了"""
        logger.info(f"输入密码: {text}")
        self.find(watch=watch).click()
        self._driver.d(focused=True).set_text(text)
        if enter is True:
            self._driver.enter()
        logger.info("输入完成")

    def clear(self, watch=None):
        logger.info("清空输入框")
        self.find(watch=watch).clear_text()
        print("清空完成")

    def assert_exists(self, timeout=3):
        logger.info(f"断言 {self._kwargs} 存在")
        status = self.exists(timeout=timeout)
        assert status, "控件不存在"

    def assert_text(self, text, timeout=3, watch=None):
        logger.info(f"断言 {self._kwargs} 文本属性包括: {text}")
        self.find(timeout=timeout, watch=watch)
        _text = self.text
        assert text in _text, f"文本属性 {_text} 不包含 {text}"


if __name__ == '__main__':
    pass







