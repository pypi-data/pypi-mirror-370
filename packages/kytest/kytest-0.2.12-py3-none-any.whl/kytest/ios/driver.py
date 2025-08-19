import time
import allure
import wda

from kytest.ios.util import IosUtil

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class Driver(object):
    """
    https://github.com/openatx/facebook-wda
    """

    def __init__(self, udid: str = None):
        if udid is None:
            self.device_id = IosUtil.get_first_device()
        else:
            self.device_id = udid
        logger.info(f"初始化ios驱动: {self.device_id}")

        self.port = int(self.device_id.split("-")[0][-4:])
        self.d = wda.USBClient(self.device_id,
                               port=self.port)
        self.util = IosUtil(self.device_id)

        if self.d.is_ready():
            logger.info('wda已就绪')
        else:
            logger.info('wda未就绪, 现在启动')
            self.util.start_wda()

    def back(self):
        logger.info("返回上一页")
        time.sleep(1)
        self.d.swipe(0, 100, 100, 100)

    def enter(self):
        logger.info("点击回车")
        self.d.send_keys("\n")

    def clear(self):
        logger.info("清空输入框")
        self.d.send_keys("")

    def input(self, text: str):
        logger.info(f"输入文本: {text}")
        self.d.send_keys(text)

    def click(self, x, y):
        logger.info(f"点击坐标: {x}, {y}")
        self.d.click(x, y)

    def swipe(self, x1, y1, x2, y2):
        """
        从x1，y1滑动到x2，y2

        @param x1:
        @param y1:
        @param x2:
        @param y2:
        @return:
        """
        logger.info(f"滑动")
        self.d.swipe(x1, y1, x2, y2)

    def shot(self, file_name=None):
        file_path = general_file_path(file_name)
        logger.info(f"截图保存至: {file_path}")
        self.d.screenshot(file_path)

        logger.info("截图上传allure报告")
        allure.attach.file(
            file_path,
            attachment_type=allure.attachment_type.PNG,
            name=f"{file_path}",
        )
        return file_path


if __name__ == '__main__':
    pass











