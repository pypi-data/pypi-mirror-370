"""
@Author: kang.yang
@Date: 2024/4/29 14:16
"""
import adbutils
from kytest.utils.log import logger


class Util:
    """后续封装一下adb命令进来"""

    def __init__(self, device_id=None):
        self.device_id = device_id
        if device_id:
            self.device = adbutils.device(serial=device_id)
        else:
            self.device = adbutils.device()

    @staticmethod
    def get_connected():
        """获取当前连接的手机列表"""
        device_list = adbutils.adb.device_list()
        if device_list:
            device_id_list = [device.serial for device in device_list]
        else:
            device_id_list = []
        if len(device_id_list) > 0:
            logger.info(f"已连接设备列表: {device_id_list}")
            return device_id_list
        else:
            raise Exception("无已连接设备")

    @staticmethod
    def get_first_device():
        """获取已连接的第一个手机"""
        return Util.get_connected()[0]

    def click(self, x, y):
        """
        点击坐标
        @param x:
        @param y:
        @return:
        """
        self.device.click(x, y)

    def swipe(self, x1, y1, x2, y2):
        """
        从x1，y1滑动到x2，y2
        @param x1:
        @param y1:
        @param x2:
        @param y2:
        @return:
        """
        self.device.swipe(x1, y1, x2, y2)

    def input(self, text):
        """
        输入
        @param text:
        @return:
        """
        self.device.send_keys(text)

    def start_app(self, pkg):
        """
        启动应用
        @param pkg:
        @return:
        """
        self.device.app_start(pkg)

    def stop_app(self, pkg):
        """
        停止应用
        @param pkg:
        @return:
        """
        self.device.app_stop(pkg)

    def clear_app(self, pkg):
        """
        清空应用缓存
        @param pkg:
        @return:
        """
        self.device.app_clear(pkg)

    def install_app(self, apk):
        """
        安装应用
        @param apk:
        @return:
        """
        self.device.install(apk)

    def uninstall_app(self, pkg):
        """
        卸载应用
        @param pkg:
        @return:
        """
        self.device.uninstall(pkg)


if __name__ == '__main__':
    util = Util()
    util.stop_app('com.qizhidao.clientapp')
