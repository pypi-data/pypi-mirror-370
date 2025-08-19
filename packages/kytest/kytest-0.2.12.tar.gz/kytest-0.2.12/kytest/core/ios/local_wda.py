"""
@Author: kang.yang
@Date: 2025/4/9 16:02
"""
import shutil
import time
import subprocess
import tidevice

from kytest.utils.common import get_free_port


class LocalWdaInit:
    """
    本地wda初始化
    """
    def __init__(self, udid: str, wda_project_path: str = None):
        self.udid = udid
        self.wda_project_path = wda_project_path

    def runner_lower_version(self):
        """
        设备系统版本小于ios17
        @return:
        """
        try:
            local_port = get_free_port()
            tidevice_path = shutil.which("tidevice")
            # 启动xctest
            xctest_cmd_str = f'{tidevice_path} -u {self.udid} xctest'
            print(xctest_cmd_str)
            p1 = subprocess.Popen(xctest_cmd_str.split())
            time.sleep(3)
            if p1.poll() is not None:
                raise Exception("xctest启动失败")
            # 启动端口转发
            proxy_cmd_str = f'{tidevice_path} -u {self.udid} relay {local_port} 8100'
            print(proxy_cmd_str)
            p2 = subprocess.Popen(proxy_cmd_str.split())
            time.sleep(3)
            if p2.poll() is not None:
                raise Exception("proxy启动失败")
            return p1, p2, f'http://localhost:{local_port}'
        except Exception as e:
            print(str(e))
            try:
                p1.kill()
                p2.kill()
            except Exception as e:
                print(str(e))

    def runner_higher_version(self):
        """
        设备系统版本大于等于ios
        @return:
        """
        try:
            # 先用xcodebuild启动xctest
            if self.wda_project_path is None:
                raise KeyError('高版本系统wda_project_path不能为None')
            xctool_path = shutil.which("xcodebuild")
            xctest_cmd_str = f"{xctool_path} -project {self.wda_project_path}" \
                             f" -scheme WebDriverAgentRunner -destination 'id={self.udid}' test"
            print(xctest_cmd_str)
            p1 = subprocess.Popen(xctest_cmd_str, shell=True)
            print("等待15秒，等本地wda启动")
            time.sleep(15)
            if p1.poll() is not None:
                raise Exception("proxy启动失败")
            # 再用tidevice转发端口
            local_port = get_free_port()
            tidevice_path = shutil.which("tidevice")
            proxy_cmd_str = f'{tidevice_path} -u {self.udid} relay {local_port} 8100'
            print(proxy_cmd_str)
            p2 = subprocess.Popen(proxy_cmd_str.split())
            time.sleep(3)
            if p2.poll() is not None:
                raise Exception("proxy启动失败")
            return p1, p2, f'http://localhost:{local_port}'
        except Exception as e:
            print(str(e))
            try:
                p1.kill()
                p2.kill()
            except Exception as e:
                print(str(e))

    def run(self):
        product_version = tidevice.Device(udid=self.udid).product_version.split('.')[0]
        print(product_version)
        if int(product_version) >= 17:
            return self.runner_higher_version()
        else:
            return self.runner_lower_version()
