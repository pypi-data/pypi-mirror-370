# 依赖通过easyocr起一个识别服务
import time

from typing import Optional, Literal

from .driver import ocr_discern

from kytest.utils.log import logger
from kytest.utils.cv_util import draw_red_by_rect


class OcrElem(object):
    """ocr识别定位"""

    def __init__(self,
                 driver=None,
                 text: str = None,
                 pos: Optional[Literal["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]] = None,
                 grade=0.8,
                 _debug: bool = False):
        """
        @param driver: 设备驱动
        @param text: 需要识别的文本
        @param pos: 把图片分成四块，TOP_LEFT、TOP_RIGHT、BOTTOM_LEFT、BOTTOM_RIGHT（左上、右上、左下、右下）
        @param grade: 置信度，最大1，越高代表准确率越高
        @param _debug: 截图并圈选位置，用于调试
        """
        self.driver = driver
        self.text = text
        self._position = pos
        self._grade = grade
        self._debug = _debug

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self.driver = instance.driver
        return self

    def find_element(self, retry=3, timeout=1):
        logger.info(f"开始查找元素: {self.text}")
        for i in range(retry):
            time.sleep(timeout)
            logger.info(f"第{i+1}次识别")
            info = self.driver.screenshot(self.text + f"_第{i+1}次识别",
                                          position=self._position)
            if self._position is not None:
                image_path = info.get("path")
            else:
                image_path = info

            res = ocr_discern(image_path, self.text)
            if res:
                x, y = res
                if self._position is not None:
                    logger.debug(self._position)
                    width = info.get("width")
                    height = info.get("height")

                    if self._position == 'TOP_RIGHT':
                        x = width / 2 + x
                    elif self._position == 'TOP_LEFT':
                        pass
                    elif self._position == 'BOTTOM_LEFT':
                        y = height / 2 + y
                    elif self._position == 'BOTTOM_RIGHT':
                        x = width / 2 + x
                        y = height / 2 + y

                x, y = int(x), int(y)
                logger.info(f'识别坐标为: ({x}, {y})')
                if self._debug is True:
                    file_path = self.driver.screenshot(f'ocr识别定位成功')
                    draw_red_by_rect(file_path,
                                     (x - 100, y - 100, 200, 200))
                return x, y
        else:
            self.driver.screenshot(f'ocr识别定位失败')
            raise Exception('通过OCR未识别指定文字或置信度过低，无法进行点击操作！')

    def exists(self, timeout=1):
        logger.info(f'ocr识别文本: {self.text} 是否存在')
        try:
            self.find_element(timeout=timeout)
        except Exception as e:
            logger.debug(str(e))
            return False
        else:
            return True

    def click(self, retry=3, timeout=3):
        logger.info(f'ocr点击文本: {self.text}')
        x, y = self.find_element(retry=retry, timeout=timeout)
        self.driver.click(x, y)
        logger.info("点击完成")


if __name__ == '__main__':
    pass




