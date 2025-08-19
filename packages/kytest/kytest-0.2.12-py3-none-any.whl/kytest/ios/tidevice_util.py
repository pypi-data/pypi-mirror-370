"""
@Author: kang.yang
@Date: 2024/4/27 14:39
"""
import time
import os
import subprocess
import shutil

from kytest.utils.log import logger
from kytest.utils.exceptions import KError


class TideviceUtil:
    """
    tidevice常用功能的封装
    """

    @staticmethod
    def get_connected():
        """获取当前连接的设备列表"""
        cmd = 'tidevice list'
        output = os.popen(cmd).read()
        device_list = [item.split(' ')[0] for item in output.split('\n') if item]
        if len(device_list) > 0:
            logger.info(f"已连接设备列表: {device_list}")
            return device_list
        else:
            raise KError(msg=f"无已连接设备")

    @staticmethod
    def uninstall_app(device_id=None, pkg_name=None):
        """卸载应用"""
        cmd = f"tidevice -u {device_id} uninstall {pkg_name}"
        logger.info(f"卸载应用: {pkg_name}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{device_id} 卸载应用{pkg_name} 成功")
            return
        else:
            logger.info(f"{device_id} 卸载应用{pkg_name}失败，因为{output}")

    @staticmethod
    def install_app(device_id=None, ipa_url=None):
        """安装应用
        """
        cmd = f"tidevice -u {device_id} install {ipa_url}"
        logger.info(f"安装应用: {ipa_url}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{device_id} 安装应用{ipa_url} 成功")
            return
        else:
            logger.info(f"{device_id} 安装应用{ipa_url}失败，因为{output}")

    @staticmethod
    def start_wda(udid: str, port, wda_bundle_id=None):
        xctool_path = shutil.which("tidevice")
        args = []
        if udid:
            args.extend(["-u", udid])
        args.append("wdaproxy")
        args.extend(["--port", str(port)])
        if wda_bundle_id is not None:
            args.extend(["-B", wda_bundle_id])
        p = subprocess.Popen([xctool_path] + args)
        time.sleep(3)
        if p.poll() is not None:
            raise KError("wda启动失败，可能是手机未连接")
