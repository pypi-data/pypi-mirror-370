import time
import threading

from kytest.utils.log import logger
from ios.driver import IosDriver, \
    TideviceUtil
from kytest.utils.common import calculate_time, \
    draw_red_by_rect
from kytest.utils.exceptions import KError
from image.element import ImgElem
from ocr import OcrElem


lock = threading.Lock()


class IosElem(object):
    """
    IOS原生元素定义
    """

    def __init__(self,
                 driver: IosDriver = None,
                 name: str = None,
                 label: str = None,
                 labelCont: str = None,
                 value: str = None,
                 valueCont: str = None,
                 text: str = None,
                 textCont: str = None,
                 className: str = None,
                 xpath: str = None,
                 image: str = None,
                 ocr: str = None,
                 region: int = None,
                 grade: float = 0.8,
                 index: int = None,
                 _debug: bool = False):
        """

        @param driver: IOS驱动
        @param name: name定位
        @param label: label定位
        @param labelCont: label模糊匹配
        @param value: value定位
        @param valueCont: value模糊匹配
        @param text: text定位，应该是包含了label、value
        @param textCont: text模糊匹配
        @param className: className定位
        @param xpath: xpath定位
        @param image: 图像识别
        @param ocr: ocr识别
        @param region: ocr识别区域设置，支持1、2、3、4
        @param grade: 识别阈值设置
        @param index: 识别到多个控件时，根据index获取其中一个
        @param _debug: 截图并圈选识别到的控件，用于调试
        """
        self._kwargs = {}
        if name is not None:
            self._kwargs["name"] = name
        if label is not None:
            self._kwargs["label"] = label
        if labelCont is not None:
            self._kwargs["labelContains"] = labelCont
        if value is not None:
            self._kwargs["value"] = value
        if valueCont is not None:
            self._kwargs["valueContains"] = valueCont
        if text is not None:
            self._kwargs["text"] = text
        if textCont is not None:
            self._kwargs["textContains"] = textCont
        if className is not None:
            self._kwargs["className"] = className
        if index is not None:
            self._kwargs["index"] = index

        self._driver = driver
        self._xpath = xpath
        self._debug = _debug
        self._image = image
        self._ocr = ocr
        self._pos = region
        self._grade = grade

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    def _match(self, text):
        """
        判断元素是否存在当前页面
        @return:
        """
        _element = self._driver.d(text=text)
        result = text if _element.wait(timeout=0.1,
                                       raise_error=False) else None
        return result

    def _watch(self, loc_list, timeout=3):
        logger.info("开始弹窗检测")
        # 多线程match，如果match到，获取第一个非None内容，进行点击
        # match完休息1s，如果休息3s也没有match到，就停止（定义一个flag，match到就清零）
        # 如果3s内仍然能match到就继续（如果flag大于3就停止）
        _build_info = ["允许", "使用App时允许", "始终允许", "同意"]
        if loc_list is True:
            loc_list = _build_info
        else:
            loc_list = list(set(_build_info + loc_list))
        flag = timeout
        while flag > 0:
            import concurrent.futures

            logger.info(f"匹配: {loc_list}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self._match, loc_list)
                results = [item for item in results if item is not None]

            if results:
                logger.info(f"匹配到: {results}")
                self._driver.d(text=results[0]).click()
                logger.info("点击成功")
                flag = timeout
            else:
                logger.info("匹配失败")

            flag -= 1
            time.sleep(1)
        logger.info("结束检测")

    @calculate_time
    def find(self, timeout=10, watch=None):
        """
        针对元素定位失败的情况，抛出KError异常
        @param timeout:
        @param watch：弹窗检测
        ["允许", "同意"]
        @return:
        """
        if watch:
            self._watch(watch)

        # if self._xpath is not None:
        #     logger.info(f'查找控件: xpath={self._xpath}')
        # else:
        #     logger.info(f'查找控件: {self._kwargs}')

        _element = self._driver.d.xpath(self._xpath) if \
            self._xpath else self._driver.d(**self._kwargs)

        try:
            if _element.wait(timeout=timeout):
                logger.info(f"查找成功")
                if self._debug is True:
                    file_path = self._driver.screenshot("查找成功")
                    rect = _element.bounds
                    scale = self._driver.d.scale
                    rect_tuple = (rect.x * scale, rect.y * scale,
                                  rect.width * scale, rect.height * scale)
                    logger.debug(rect_tuple)
                    draw_red_by_rect(file_path, rect_tuple)
                return _element
            else:
                logger.info(f"查找失败")
                self._driver.screenshot("查找失败")
                raise KError(f"控件 {self._kwargs} 查找失败")
        except ConnectionError:
            logger.info('wda连接失败, 进行重连!!!')
            # 由于WDA会意外链接错误
            for i in range(5):
                try:
                    TideviceUtil.start_wda(self._driver.device_id,
                                           port=self._driver.port)
                    if self._driver.d.is_ready():
                        logger.info('wda启动成功')
                    else:
                        raise KError('wda启动失败，可能是WebDriverAgent APP端证书失效!')
                    break
                except Exception as e:
                    logger.info("启动wda异常，重试!!!")
                    logger.info(str(e))
                    continue

            logger.info('重连成功, 重新开始查找控件')
            if _element.wait(timeout=timeout):
                logger.info(f"查找成功")
                return _element
            else:
                logger.info(f"查找失败")
                self._driver.screenshot("查找失败")
                raise KError(f"控件 {self._kwargs} 查找失败")

    def text(self):
        """获取元素文本"""
        logger.info(f"获取 {self._kwargs} 文本属性")
        text = [elem.text for elem in self.find(timeout=5).find_elements()]
        logger.info(text)
        return text

    def exists(self, timeout=5):
        """
        判断元素是否存在当前页面
        @param timeout:
        @return:
        """
        logger.info(f"检查 {self._kwargs} 是否存在")
        if self._image is not None:
            return ImgElem(self._driver,
                           file=self._image,
                           scale=self._driver.d.scale,
                           grade=self._grade,
                           _debug=self._debug).exists(timeout=timeout)
        elif self._ocr is not None:
            return OcrElem(self._driver,
                           text=self._ocr,
                           pos=self._pos,
                           grade=self._grade,
                           _debug=self._debug).exists(timeout=timeout)
        else:
            result = False
            try:
                _element = self.find(timeout=timeout)
                result = True
            except:
                result = False
            finally:
                logger.info(result)
                return result

    def _adapt_center(self, timeout=5, watch=None):
        """
        修正控件中心坐标
        """
        bounds = self.find(timeout=timeout, watch=watch).bounds
        left_top_x, left_top_y, width, height = \
            bounds.x, bounds.y, bounds.width, bounds.height
        center_x = int(left_top_x + width/2)
        center_y = int(left_top_y + height/2)
        logger.info(f'{center_x}, {center_y}')
        return center_x, center_y

    def click(self, timeout=5, watch=None):
        """
        单击
        @param: retry，重试次数
        @param: timeout，每次重试超时时间
        """
        logger.info(f'点击 {self._kwargs}')

        def _click():
            if self._image is not None:
                ImgElem(self._driver,
                        file=self._image,
                        scale=self._driver.d.scale,
                        grade=self._grade,
                        _debug=self._debug).click(timeout=timeout)
            elif self._ocr is not None:
                OcrElem(self._driver,
                        text=self._ocr,
                        pos=self._pos,
                        grade=self._grade,
                        _debug=self._debug).click(timeout=timeout)
            else:
                x, y = self._adapt_center(timeout=timeout, watch=watch)
                self._driver.d.appium_settings({"snapshotMaxDepth": 0})
                self._driver.d.tap(x, y)
                self._driver.d.appium_settings({"snapshotMaxDepth": 50})

        count = 0
        while count < 5:
            if count > 1:
                logger.info(f"操作失败，第{count}次重试.")
            try:
                _click()
            except Exception as e:
                logger.debug(str(e))
                time.sleep(3)
                count += 1
                continue
            else:
                break
        else:
            logger.info("重试5次仍然失败.")

    def click_exists(self, timeout=5):
        logger.info(f"{self._kwargs} 存在才点击")
        if self.exists(timeout=timeout):
            self.click()

    def clear(self):
        """清除文本"""
        logger.info("清除输入框文本")
        self.find().clear_text()

    def input(self, text, enter=False):
        """输入内容"""
        logger.info(f"输入文本：{text}")
        self.find().set_text(text)
        if enter is True:
            self._driver.enter()

    def input_exists(self, text: str, timeout=5, enter=False):
        logger.info(f"{self._kwargs} 存在才输入: {text}")
        if self.exists(timeout=timeout):
            self.input(text, enter=enter)
            logger.info("输入成功")
        else:
            logger.info("控件不存在")

    def assert_exists(self, timeout=3):
        logger.info(f"断言 {self._kwargs} 存在")
        status = self.exists(timeout=timeout)
        assert status, f"控件不存在"

    def assert_text(self, text, timeout=3):
        logger.info(f"断言 {self._kwargs} 文本属性包括: {text}")
        self.find(timeout=timeout)
        _text = self.text
        assert text in _text, f"文本属性 {_text} 不包含 {text}"


if __name__ == '__main__':
    pass

















