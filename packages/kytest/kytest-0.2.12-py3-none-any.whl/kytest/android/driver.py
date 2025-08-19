import os
import re
import time
import adbutils
import subprocess
import requests
import six
import uiautomator2 as u2

from kytest.utils.log import logger
from kytest.utils.exceptions import KError
# from kytest.utils.common import general_file_path, cut_and_upload


def connected():
    """获取当前连接的手机列表"""
    # cmd = 'adb devices'
    # output = os.popen(cmd).read()
    # device_list = [item.split('\t')[0] for item in
    #                output.split('\n') if item.endswith('device')]
    device_list = adbutils.adb.device_list()
    if device_list:
        device_id_list = [device.serial for device in device_list]
    else:
        device_id_list = []
    if len(device_id_list) > 0:
        logger.info(f"已连接设备列表: {device_id_list}")
        return device_id_list
    else:
        raise KError(msg=f"无已连接设备")


class AdrDriver(object):

    def __init__(self, serial=None, package=None):
        logger.info(f"初始化安卓驱动: {serial}")

        self.pkg_name = package
        self.device_id = serial

        # 未传设备id就获取usb默认连接的第一个设备
        if self.device_id is None:
            self.device_id = connected()[0]

        self.d = u2.connect(self.device_id)

        if not self.d.alive:
            """判断uiautomator服务是否正常运行，否则重启它"""
            logger.info("uiautomator异常，进行重启！！！")
            self.d.healthcheck()
        else:
            logger.info("uiautomator已就绪")

    def assert_act(self, activity_name: str, timeout=5):
        logger.info(f"断言 activity 等于 {activity_name}")
        assert self.d.wait_activity(activity_name, timeout=timeout)

    def uninstall_app(self, pkg_name=None):
        logger.info(f"卸载应用")
        if pkg_name is not None:
            self.pkg_name = pkg_name
        if self.pkg_name is None:
            raise KeyError("应用包名不能为空")
        self.d.app_uninstall(self.pkg_name)

    @staticmethod
    def download_apk(src):
        """下载安装包"""
        start = time.time()
        if isinstance(src, six.string_types):
            if re.match(r"^https?://", src):
                logger.info(f'下载中...')
                file_path = os.path.join(os.getcwd(), src.split('/')[-1])
                r = requests.get(src, stream=True)
                if r.status_code != 200:
                    raise IOError(
                        "Request URL {!r} status_code {}".format(src, r.status_code))
                with open(file_path, 'wb') as f:
                    f.write(r.content)
                end = time.time()
                logger.info(f'下载成功: {file_path}，耗时: {end - start}s')
                return file_path
            elif os.path.isfile(src):
                return src
            else:
                raise IOError("static {!r} not found".format(src))

    def install_app(self, apk_path, auth=True, new=True, helper: list = None, pkg_name=None):
        """
        安装应用，push改成adb命令之后暂时无法支持远程手机调用
        @param pkg_name:
        @param apk_path: 安装包链接，支持本地路径以及http路径
        @param auth: 是否进行授权
        @param new: 是否先卸载再安装
        @param helper：install命令后的各品牌机型适配
        [
            ["assert", {"text": "未发现风险"}],
            ["click", {"text": "继续安装"}],
            ["click", {"text": "完成"}],
            ["input", {"resourceId": "xxx"}, "yyy"]
        ]
        """
        start = time.time()
        logger.info(f"安装应用: {apk_path}")
        # 卸载
        if new is True:
            if pkg_name is not None:
                self.pkg_name = pkg_name
            if self.pkg_name is None:
                raise KeyError("应用包名不能为空")
            self.uninstall_app()

        # 下载
        try:
            source = self.download_apk(apk_path)
        except:
            raise KeyError("下载apk失败")

        # 安装
        try:
            cmd_list = ['adb', 'install', "-r", "-t", source]
            if auth is True:
                cmd_list.insert(4, '-g')
            logger.debug(f"{' '.join(cmd_list)}")
            process = subprocess.Popen(cmd_list,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            if helper is None:
                # 等待子进程执行完成
                process.wait()
        except:
            raise KeyError("adb安装失败")

        # 各品牌机型适配
        try:
            if helper is not None:
                for step in helper:
                    method = step[0]
                    loc = step[1]
                    if method == "click":
                        self.d(**loc).click()
                    elif method == "assert":
                        assert self.d(**loc).wait(timeout=10)
                    elif method == "input":
                        content = step[2]
                        self.d(**loc).send_keys(content)
                    else:
                        raise KeyError("不支持的方法")
        except:
            raise KeyError("安装过程处理失败")

        # 删除下载的安装包
        if 'http' in apk_path:
            os.remove(source)

        end = time.time()
        logger.info(f'安装成功，耗时: {end - start}s')

    def start_app(self, pkg_name: str = None, stop=True):
        """启动应用
        @param pkg_name:
        @param stop: 是否先关闭应用再启动
        """
        logger.info(f"启动应用")
        if pkg_name is not None:
            self.pkg_name = pkg_name
        if self.pkg_name is None:
            raise KeyError("应用包名不能为空")

        self.d.app_start(self.pkg_name,
                         stop=stop,
                         use_monkey=True)

    def current_app(self):
        return self.d.app_current()["package"]

    def stop_app(self, pkg_name: str = None):
        logger.info("关闭应用")
        if pkg_name is not None:
            self.pkg_name = pkg_name
        if self.pkg_name is None:
            raise KeyError("应用包名不能为空")

        self.d.app_stop(self.pkg_name)

    def general_file_path(self, file_name):
        logger.info("开始截图")
        if not file_name:
            raise ValueError("文件名不能为空")

        # 截图并保存到当前目录的image文件夹中
        relative_path = "screenshot"
        # 把文件名处理成test.png的样式
        if "." in file_name:
            file_name = file_name.split(r".")[0]
        if os.path.exists(relative_path) is False:
            os.mkdir(relative_path)

        time_str = time.strftime(f"%Y%m%d%H%M%S")
        file_name = f"{time_str}_{file_name}.jpg"
        file_path = os.path.join(relative_path, file_name)
        return file_path

    def screenshot(self, file_name=None):
        file_path = self.general_file_path(file_name)
        self.d.screenshot(file_path)
        logger.info(f"保存至: {file_path}")
        return file_path

    def back(self):
        logger.info("返回上一页")
        self.d.press('back')

    def enter(self):
        logger.info("点击回车")
        self.d.press("enter")

    def input(self, text, enter=False):
        logger.info(f"输入文本: {text}")
        self.d.send_keys(text)
        if enter is True:
            self.enter()

    def click(self, x, y):
        logger.info(f"点击坐标: {x}, {y}")
        self.d.click(x, y)

    def click_alerts(self, alert_list: list):
        logger.info(f"点击弹窗: {alert_list}")
        with self.d.watch_context() as ctx:
            for alert in alert_list:
                ctx.when(alert).click()
            ctx.wait_stable()

    def swipe(self, direction: str = None):
        logger.info(f"swipe {direction}")
        key_range = ["left", "right", "up", "down"]
        if direction not in key_range:
            raise KeyError(f"direction取值只能是 {key_range} 其中一个")
        self.d.swipe_ext(direction)

    def swipe_up(self):
        self.swipe("up")

    def swipe_down(self):
        self.swipe("down")

    def swipe_left(self):
        self.swipe("left")

    def swipe_right(self):
        self.swipe("right")


if __name__ == '__main__':
    pass















