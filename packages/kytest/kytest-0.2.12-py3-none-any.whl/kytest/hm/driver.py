"""
@Author: kang.yang
@Date: 2024/9/30 10:48
"""
import allure
from hmdriver2.driver import Driver
from hmdriver2.proto import DisplayRotation

from kytest.hm.util import HmUtil

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class HmDriver:
    """
    https://github.com/codematrixer/hmdriver2
    """

    def __init__(self, device_id: str = None):
        if device_id is None:
            self.d = Driver(HmUtil.get_first_device())
        else:
            self.d = Driver(device_id)

    # app管理
    def install_app(self, *args, **kwargs):
        logger.info("安装应用")
        self.d.install_app(*args, **kwargs)

    def uninstall_app(self, *args, **kwargs):
        logger.info("卸载应用")
        self.d.uninstall_app(*args, **kwargs)

    def list_apps(self):
        logger.info("获取应用列表")
        return self.d.list_apps()

    def start_app(self, pkg_name, page_name, force=True):
        """
        可以通过hdc命令获取hdc shell aa dump -l，如 ：
        (venv) iMac:kytest_project UI$ hdc shell aa dump -l
        User ID #100
          current mission lists:{
            Mission ID #98  mission name #[#com.qzd.hm:entry:EntryAbility]  lockedState #0  mission affinity #[]
              AbilityRecord ID #2043
                app name [com.qzd.hm]
                main name [EntryAbility]
                bundle name [com.qzd.hm]
                ability type [PAGE]
                state #FOREGROUND  start time [268869923]
                app state #FOREGROUND
                ready #1  window attached #0  launcher #0
                callee connections:
                isKeepAlive: false
         }


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

    def clear_app(self, *args, **kwargs):
        logger.info("清除app数据")
        self.d.clear_app(*args, **kwargs)

    def app_info(self, *args, **kwargs):
        logger.info("获取App详情")
        return self.d.get_app_info(*args, **kwargs)

    # 设备操作
    def device_info(self):
        logger.info("获取设备信息")
        return self.d.device_info

    def device_size(self):
        logger.info("获取设备分辨率")
        return self.d.display_size

    def rotation_status(self):
        logger.info("获取设备旋转状态")
        return self.d.display_rotation

    def set_rotation(self, status: int):
        """
        需要app支持旋转
        @param status:
        @return:
        """
        logger.info("设置设备旋转状态")
        if status == 0:
            self.d.set_display_rotation(DisplayRotation.ROTATION_0)
        elif status == 1:
            self.d.set_display_rotation(DisplayRotation.ROTATION_90)
        elif status == 2:
            self.d.set_display_rotation(DisplayRotation.ROTATION_180)
        elif status == 4:
            self.d.set_display_rotation(DisplayRotation.ROTATION_270)

    def home(self):
        logger.info("返回桌面首页")
        self.d.go_home()

    def back(self):
        logger.info("返回上一页")
        self.d.go_back()

    def screen_on(self):
        logger.info("点亮屏幕")
        self.d.screen_on()

    def screen_off(self):
        logger.info("息屏")
        self.d.screen_off()

    def unlock(self):
        logger.info("屏幕解锁")
        self.d.unlock()

    def press(self, key_code):
        """
        https://github.com/codematrixer/hmdriver2/blob/4d7bceaded947bd63d737de180064679ad4c77b8/hmdriver2/proto.py#L133
        @param key_code:
        @return:
        """
        logger.info("系统按键点击")
        self.d.press_key(key_code)

    def shell(self, *args, **kwargs):
        logger.info("执行hdc shell 命令")
        self.d.shell(*args, **kwargs)

    def open_url(self, url):
        logger.info("打开url或schema")
        self.d.open_url(url)

    def pull(self, *args, **kwargs):
        logger.info("从设备下载文件到本地")
        self.d.pull_file(*args, **kwargs)

    def push(self, *args, **kwargs):
        logger.info("将本地文件上传到设备")
        self.d.push_file(*args, **kwargs)

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
        logger.info("点击操作")
        self.d.click(x, y)

    def double_click(self, x, y):
        logger.info("双击操作")
        self.d.double_click(x, y)

    def long_click(self, x, y):
        logger.info("长按操作")
        self.d.long_click(x, y)

    def swipe(self, *args, **kwargs):
        logger.info("滑动操作")
        self.d.swipe(*args, **kwargs)

    def input(self, *args, **kwargs):
        logger.info("输入操作")
        self.d.input_text(*args, **kwargs)

    def dump(self):
        logger.info("获取控件树")
        return self.d.dump_hierarchy()


if __name__ == '__main__':
    dr = HmDriver()
    dr.start_app('com.qzd.hm', 'EntryAbility')


