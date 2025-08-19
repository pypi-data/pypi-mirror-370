import allure
import uiautomator2 as u2

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class Driver:
    """
    u2库代码地址：https://github.com/openatx/uiautomator2
    """

    def __init__(self, serial: str, package: str = None):
        """
        @param serial: 设备序列号，通过adb devices获取，或者通过关于手机-序列号获取
        @param package: 应用包名，通过adb shell pm list packages获取
        """
        logger.info(f"初始化本地设备连接: {serial}")
        self.package = package
        self.d = u2.connect(serial)

    def uninstall_app(self, package: str = None):
        """
        卸载应用
        @param package: 应用包名
        @return:
        """
        if self.package is None:
            if package is None:
                raise KeyError('package不能为空')
            else:
                self.package = package
        logger.info(f"卸载应用: {self.package}")
        self.d.app_uninstall(self.package)

    def install_app(self, apk_url, package: str = None):
        """
        安装应用
        @param apk_url: apk链接
        @param package: 应用包名
        @return:
        """
        if self.package is None:
            if package is None:
                raise KeyError('package不能为空')
            else:
                self.package = package
        self.d.app_uninstall(self.package)
        logger.info(f"安装应用: {apk_url}")
        self.d.app_install(apk_url)

    def start_app(self, package: str = None):
        """
        启动应用
        @param package: 应用包名
        @return:
        """
        if self.package is None:
            if package is None:
                raise KeyError('package不能为空')
            else:
                self.package = package
        logger.info(f"启动应用: {self.package}")
        self.d.app_start(package_name=self.package, use_monkey=True)

    def stop_app(self, package: str = None):
        """
        停止应用
        @param package: 应用包名
        @return:
        """
        if self.package is None:
            if package is None:
                raise KeyError('package不能为空')
            else:
                self.package = package
        logger.info(f"停止应用: {self.package}")
        self.d.app_stop(self.package)

    def shot(self, file_name: str = None):
        """
        截图
        @param file_name: 截图保存后的文件名
        @return:
        """
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

    def click(self, x, y):
        """
        点击坐标
        @param x: 横坐标
        @param y: 纵坐标
        @return:
        """
        self.d.click(x, y)

    def input(self, *args, **kwargs):
        """
        输入
        @param args:
        @param kwargs:
        @return:
        """
        self.d.send_keys(*args, **kwargs)

    def unlock(self):
        """
        设备解锁
        @return:
        """
        self.d.unlock()

    def shell(self, *args, **kwargs):
        """
        执行adb shell
        @param args:
        @param kwargs:
        @return:
        """
        self.d.shell(*args, **kwargs)
























