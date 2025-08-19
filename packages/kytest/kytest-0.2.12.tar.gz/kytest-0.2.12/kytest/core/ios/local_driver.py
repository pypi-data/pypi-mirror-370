"""
@Author: kang.yang
@Date: 2025/4/9 16:03
"""
import allure
import wda
import time
import subprocess

from .local_wda import LocalWdaInit

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class Driver(object):
    """
    https://github.com/openatx/facebook-wda
    """

    def __init__(
            self,
            udid: str,
            bundle_id: str = None,
            wda_project_path: str = None,
        ):
        """
        手机udid
        @param udid: tidevice list获取
        @param bundle_id: tidevice applist获取
        @param wda_project_path: wda工程入口文件路径
        """
        self.udid = udid
        self.bundle_id = bundle_id
        logger.info(f"初始化本地wda: {udid}")
        process1, process2,  wda_url = LocalWdaInit(udid, wda_project_path).run()
        print(wda_url)
        self.p1, self.p2 = process1, process2
        self.d = wda.Client(wda_url)
        if self.d.is_ready():
            logger.info('wda已就绪')
        else:
            logger.info('wda未就绪, 请检查wda服务')

    def uninstall_app(self, bundle_id: str = None):
        """
        卸载应用
        @return:
        """
        if self.bundle_id is None:
            if bundle_id is None:
                raise KeyError('bundle_id不能为空')
            else:
                self.bundle_id = bundle_id

        cmd = f"tidevice -u {self.udid} uninstall {self.bundle_id}"
        print(cmd)
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{self.udid} 卸载应用成功")
            return
        else:
            logger.info(f"{self.udid} 卸载应用成功")

    def install_app(self, ipa_url, bundle_id: str = None):
        """
        安装应用
        @param ipa_url:
        @param bundle_id
        @return:
        """
        if self.bundle_id is None:
            if bundle_id is None:
                raise KeyError('bundle_id不能为空')
            else:
                self.bundle_id = bundle_id
        self.uninstall_app(self.bundle_id)

        cmd = f"tidevice -u {self.udid} install {ipa_url}"
        print(cmd)
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{self.udid} 安装应用成功")
            return
        else:
            logger.info(f"{self.udid} 安装应用失败")

    def start_app(self, bundle_id: str = None):
        """
        启动应用
        @return:
        """
        if self.bundle_id is None:
            if bundle_id is None:
                raise KeyError('bundle_id不能为空')
            else:
                self.bundle_id = bundle_id
        logger.info(f"启动应用: {self.bundle_id}")
        self.d.app_start(self.bundle_id)

    def stop_app(self, bundle_id: str = None):
        """
        停止应用
        @return:
        """
        if self.bundle_id is None:
            if bundle_id is None:
                raise KeyError('bundle_id不能为空')
            else:
                self.bundle_id = bundle_id
        logger.info(f"停止应用: {self.bundle_id}")
        self.d.app_stop(self.bundle_id)

    def close(self):
        """
        清除xctest和relay进程
        @return:
        """
        try:
            self.p1.kill()
            self.p2.kill()
        except Exception as e:
            print(str(e))

    def input(self, text: str):
        self.d.send_keys(text)

    def click(self, x, y):
        self.d.click(x, y)

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

    def scale(self):
        return self.d.scale

    def unlock(self):
        self.d.unlock()

    def _match(self, text):
        """
        判断元素是否存在当前页面
        @return:
        """
        _element = self.d(text=text)
        result = text if _element.wait(timeout=0.1,
                                       raise_error=False) else None
        return result

    def pop_check(self, watch_list: list, timeout=3):
        logger.info(f"开始弹窗检测: {watch_list}")
        # 多线程match，如果match到，获取第一个非None内容，进行点击
        # match完休息1s，如果休息3s也没有match到，就停止（定义一个flag，match到就清零）
        # 如果3s内仍然能match到就继续（如果flag大于3就停止）
        _build_info = ["允许", "使用App时允许", "始终允许"]
        if watch_list is True:
            loc_list = _build_info
        else:
            loc_list = list(set(_build_info + watch_list))
        flag = timeout
        while flag > 0:
            import concurrent.futures

            logger.info(f"匹配: {loc_list}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self._match, loc_list)
                results = [item for item in results if item is not None]

            if results:
                logger.info(f"匹配到: {results}")
                try:
                    self.d(text=results[0]).click_exists(timeout=1)
                except:
                    pass
                logger.info("点击成功")
                flag = timeout
            else:
                logger.info("匹配失败")

            flag -= 1
            time.sleep(1)
        logger.info("结束检测")
