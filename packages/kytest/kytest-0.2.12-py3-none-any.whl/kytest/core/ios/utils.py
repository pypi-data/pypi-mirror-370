"""
@Author: kang.yang
@Date: 2024/4/27 14:39
"""
import time
import os
import subprocess
import shutil

from kytest.utils.log import logger


class Utils:
    """
    tidevice常用功能的封装
    """

    def __init__(self, device_id=None):
        self.device_id = device_id

    @staticmethod
    def get_all_device():
        """获取当前连接的设备列表"""
        cmd = 'tidevice list'
        output = os.popen(cmd).read()
        device_list = [item.split(' ')[0] for item in output.split('\n') if item]
        if len(device_list) > 0:
            logger.info(f"已连接设备列表: {device_list}")
            return device_list
        else:
            raise Exception("无已连接设备")

    @staticmethod
    def get_first_device():
        """获取当前连接的第一个设备"""
        return Utils.get_all_device()[0]

    def uninstall_app(self, pkg_name):
        """卸载应用"""
        if self.device_id is None:
            cmd = f"tidevice uninstall {pkg_name}"
        else:
            cmd = f"tidevice -u {self.device_id} uninstall {pkg_name}"

        logger.info(f"卸载应用: {pkg_name}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{self.device_id} 卸载应用{pkg_name} 成功")
            return
        else:
            logger.info(f"{self.device_id} 卸载应用{pkg_name}失败，因为{output}")

    def install_app(self, ipa_url):
        """
        安装应用
        """
        if self.device_id is None:
            cmd = f"tidevice install {ipa_url}"
        else:
            cmd = f"tidevice -u {self.device_id} install {ipa_url}"

        logger.info(f"安装应用: {ipa_url}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{self.device_id} 安装应用{ipa_url} 成功")
            return
        else:
            logger.info(f"{self.device_id} 安装应用{ipa_url}失败，因为{output}")

    def start_wda(self, wda_bundle_id=None):
        """
        启动wda
        @param wda_bundle_id:
        @return:
        """
        xctool_path = shutil.which("tidevice")
        args = []
        if self.device_id is not None:
            args.extend(["-u", self.device_id])
        args.append("wdaproxy")
        port = int(self.device_id.split("-")[0][-4:])
        args.extend(["--port", str(port)])
        if wda_bundle_id is not None:
            args.extend(["-B", wda_bundle_id])
        p = subprocess.Popen([xctool_path] + args)
        time.sleep(3)
        if p.poll() is not None:
            raise Exception("wda启动失败，可能是手机未连接")

    def start_app(self, pkg_name):
        """启动应用"""
        if self.device_id is None:
            cmd = f"tidevice launch {pkg_name}"
        else:
            cmd = f"tidevice -u {self.device_id} launch {pkg_name}"

        logger.info(f"启动应用: {pkg_name}")
        output = subprocess.getoutput(cmd)
        print(output)

    def stop_app(self, pkg_name):
        """杀掉应用"""
        if self.device_id is None:
            cmd = f"tidevice kill {pkg_name}"
        else:
            cmd = f"tidevice -u {self.device_id} kill {pkg_name}"

        print(cmd)
        logger.info(f"杀掉应用: {pkg_name}")
        output = subprocess.getoutput(cmd)
        print(output)







