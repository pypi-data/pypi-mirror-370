"""
@Author: kang.yang
@Date: 2024/9/30 10:53
"""
import os
from kytest.utils.log import logger


class HmUtil:

    @staticmethod
    def get_connected():
        """
        获取设备列表
        @return:
        """
        cmd = 'hdc list targets'
        output = os.popen(cmd).read()
        print(output)
        device_list = [item.split(' ')[0] for item in output.split('\n') if item]
        if len(device_list) > 0:
            logger.info(f"已连接设备列表: {device_list}")
            return device_list
        else:
            raise Exception("无已连接设备")

    @staticmethod
    def get_first_device():
        """
        获取第一个设备
        @return:
        """
        return HmUtil.get_connected()[0]


if __name__ == '__main__':
    print(HmUtil.get_first_device())
