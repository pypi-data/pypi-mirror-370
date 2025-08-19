"""
@Author: kang.yang
@Date: 2024/4/29 14:16
"""
from adbutils import adb


class AdrUtil:
    """
    单独拆开的原因是，有一些功能单独这个库就可以实现了，不用初始化
    https://github.com/openatx/adbutils
    """

    def __init__(self, device_id=None):
        if device_id is None:
            self.device = adb.device()
        else:
            self.device = adb.device(device_id)

    @staticmethod
    def get_connected():
        """
        获取设备列表
        @return:
        """
        device_list = adb.device_list()
        if device_list:
            return [device.serial for device in device_list]
        else:
            raise Exception("无已连接设备")

    @staticmethod
    def get_first_device():
        """
        获取第一个设备
        @return:
        """
        return AdrUtil.get_connected()[0]

    def shell(self, *args, **kwargs):
        """
        执行adb shell命令
        @param args:
        @param kwargs:
        @return: : ShellReturn(args='echo 1', returncode=0, output='1\n')
        """
        return self.device.shell2(*args, **kwargs)

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

    def start_app(self, pkg, stop=True):
        """
        启动应用
        @param pkg:
        @param stop: 是否默认先关闭应用
        @return:
        """
        if stop is True:
            self.stop_app(pkg)
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

    def install_app(self, apk, grant=True, nolaunch=False):
        """
        安装应用
        @param apk:
        @param grant：是否授予全部权限
        @param nolaunch：默认安装后直接启动应用
        @return:
        """
        flags = ["-r", "-t"]
        if grant is True:
            flags.append("-g")
        self.device.install(apk, flags=flags, nolaunch=nolaunch)

    def uninstall_app(self, pkg):
        """
        卸载应用
        @param pkg:
        @return:
        """
        self.device.uninstall(pkg)

    def running_apps(self):
        """
        运行中的应用列表
        @return:
        """
        return self.device.list_packages()

    def current_app(self):
        """
        当前应用
        @return:
        """
        return self.device.app_current()

    def push(self, *args, **kwargs):
        """
        推送内容到手机
        @param args:
        @param kwargs:
        @return:
        """
        self.device.sync.push(*args, **kwargs)

    def pull(self, *args, **kwargs):
        """
        从手机下载内容
        @param args:
        @param kwargs:
        @return:
        """
        self.device.sync.pull(*args, **kwargs)

    def app_info(self, pkg_name: str):
        """
        应用版本信息等
        @param pkg_name:
        @return:
        """
        return self.device.app_info(pkg_name)

    def device_info(self):
        """
        设备信息
        @return:
        """
        return self.device.info

    def window_size(self):
        return self.device.window_size()

    def press(self, key_code):
        """
        键盘点击
        @param key_code: HOME，详见：https://www.cnblogs.com/hujingnb/p/10282238.html
        @return:
        """
        self.device.keyevent(key_code)

    def dump(self):
        return self.device.dump_hierarchy()


if __name__ == '__main__':
    util = AdrUtil()







