import allure
import uiautomator2 as u2

from kytest.adr.util import AdrUtil

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class Driver:
    """
    https://github.com/openatx/uiautomator2
    """

    def __init__(self, device_id=None):
        if device_id is None:
            device_id = AdrUtil.get_first_device()
        logger.info(f"初始化安卓驱动: {device_id}")

        self.d = u2.connect(device_id)
        self.util = AdrUtil(device_id)

    def shot(self, file_name=None):
        """
        比adb截图快，所以保留了
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

    def wait_app(self, pkg_name: str, front=False, timeout=20):
        """
        等待app运行
        @param pkg_name:
        @param front：应用保持在前台
        @param timeout：
        @return:
        """
        pid = self.d.app_wait(pkg_name, front=front, timeout=timeout)
        return pid

    def open_schema(self, schema: str):
        """
        # same as
        # adb shell am start -a android.intent.action.VIEW -d "appname://appnamehost"
        @param schema:
        @return:
        """
        self.d.open_url(schema)

    def session(self, *args, **kwargs):
        """
        Session represent an app lifecycle. Can be used to start app, detect app crash.

        # Launch and close app
        sess = d.session("com.netease.cloudmusic") # start 网易云音乐
        sess.close() # 停止网易云音乐
        sess.restart() # 冷启动网易云音乐

        # Use python with to launch and close app
        with d.session("com.netease.cloudmusic") as sess:
            sess(text="Play").click()

        # Attach to the running app
        # launch app if not running, skip launch if already running
        sess = d.session("com.netease.cloudmusic", attach=True)

        # Detect app crash
        # When app is still running
        sess(text="Music").click() # operation goes normal

        # If app crash or quit
        sess(text="Music").click() # raise SessionBrokenError
        # other function calls under session will raise SessionBrokenError too

        # check if session is ok.
        # Warning: function name may change in the future
        sess.running() # True or False
        @return:
        """
        return self.d.session(*args, **kwargs)

    def wait_activity(self, activity, timeout=10):
        """
        等待activity启动
        @param activity
        @param timeout
        @return: True or False
        """
        return self.d.wait_activity(activity, timeout)

    def assert_activity(self, activity, timeout=10):
        logger.info(f"断言页面activity: {activity}")
        assert self.wait_activity(activity, timeout=timeout)

    def device_info(self):
        return self.d.device_info

    def press(self, *args, **kwargs):
        self.d.press(*args, **kwargs)

    def unlock(self):
        self.d.unlock()

    def double_click(self, *args, **kwargs):
        self.d.double_click(*args, **kwargs)

    def long_click(self, *args, **kwargs):
        self.d.long_click(*args, **kwargs)

    def drag(self, *args, **kwargs):
        self.d.drag(*args, **kwargs)

    def dump_hierarchy(self, *args, **kwargs):
        return self.d.dump_hierarchy(*args, **kwargs)

    def input(self, *args, **kwargs):
        self.d.send_keys(*args, **kwargs)


if __name__ == '__main__':
    dr = Driver()
    print(dr.d.info)






















