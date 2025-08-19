"""
@Author: kang.yang
@Date: 2024/9/30 10:48
"""
import allure

from hmdriver2.driver import Driver
from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class HmDriver:
    """
    https://github.com/codematrixer/hmdriver2
    """

    def __init__(self, device_id: str = None):
        self.d = Driver(device_id)

    # app管理
    def install_app(self, *args, **kwargs):
        logger.info("安装应用")
        self.d.install_app(*args, **kwargs)

    def uninstall_app(self, *args, **kwargs):
        logger.info("卸载应用")
        self.d.uninstall_app(*args, **kwargs)

    def start_app(self, pkg_name, page_name, force=True):
        """
        可以通过hdc命令获取hdc shell aa dump -l，如 ：
        (venv) iMac:kytest_project UI$ hdc shell aa dump -l
        @param force: 是否强制启动
        @param pkg_name: 包名，对应bundle name
        @param page_name: 页面名，对应main name
        @return:
        """
        logger.info("启动应用")
        if force is True:
            self.d.force_start_app(pkg_name, page_name)
        else:
            self.d.start_app(pkg_name, page_name)

    def stop_app(self, *args, **kwargs):
        logger.info("停止应用")
        self.d.stop_app(*args, **kwargs)

    def unlock(self):
        logger.info("屏幕解锁")
        self.d.unlock()

    def shell(self, *args, **kwargs):
        logger.info("执行hdc shell 命令")
        self.d.shell(*args, **kwargs)

    def shot(self, file_name=None):
        """
        截图并上传allure
        @param file_name:
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
        self.d.click(x, y)

    def input(self, *args, **kwargs):
        self.d.input_text(*args, **kwargs)

    def get_page_xml(self):
        return self.d.dump_hierarchy()


if __name__ == '__main__':
    dr = HmDriver()
    dr.start_app('com.qzd.hm', 'EntryAbility')


