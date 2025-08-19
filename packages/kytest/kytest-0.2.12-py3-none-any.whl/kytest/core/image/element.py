import time

from kytest.utils.log import logger
from image.driver import ImageDiscern
from kytest.utils.common import draw_red_by_rect


class ImgElem(object):
    """图像识别定位"""

    def __init__(self,
                 driver=None,
                 file: str = None,
                 scale: int = None,
                 grade=0.9,
                 gauss_num=111,
                 _debug: bool = False):
        """

        @param driver: 设备驱动
        @param file: 图片文件路径
        @param scale: 用于IOS端缩放设置
        @param grade: 识别阈值设置
        @param gauss_num: 识别的次数
        @param _debug: 截图并圈选位置，用于调试
        """
        self.driver = driver
        self.target_image = file
        self._debug = _debug
        self._scale = scale
        self._grade = grade
        self._gauss_num = gauss_num

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self.driver = instance.driver
        return self

    def exists(self, timeout=1):
        logger.info(f'图像识别判断: {self.target_image} 是否存在')
        time.sleep(timeout)
        source_image = self.driver.screenshot("图像识别中")
        res = ImageDiscern(self.target_image,
                           source_image,
                           self._grade,
                           self._gauss_num).get_coordinate()
        logger.debug(res)
        if isinstance(res, tuple):
            return True
        else:
            return False

    def click(self, retry=3, timeout=3):
        logger.info(f'图像识别点击图片: {self.target_image}')
        for i in range(retry):
            time.sleep(timeout)
            logger.info(f'第{i + 1}次查找:')
            source_image = self.driver.screenshot("图像控件")
            res = ImageDiscern(self.target_image,
                               source_image,
                               self._grade,
                               self._gauss_num).get_coordinate()
            if isinstance(res, tuple):
                logger.info(f'识别坐标为: {res}')
                x, y = res[0], res[1]
                if self._scale is not None:
                    """iphone的scale是3"""
                    x, y = int(x/self._scale), int(y/self._scale)
                if self._debug is True:
                    file_path = self.driver.screenshot('图像识别定位成功')
                    if self._scale is not None:
                        _x, _y = x * self._scale, y * self._scale
                        draw_red_by_rect(file_path,
                                         (int(_x) - 100, int(_y) - 100, 200, 200))
                    draw_red_by_rect(file_path,
                                     (int(x) - 100, int(y) - 100, 200, 200))
                self.driver.click(x, y)
                return
        else:
            self.driver.screenshot(f'图像识别定位失败')
            raise Exception('未识别到图片，无法进行点击')


if __name__ == '__main__':
    pass


