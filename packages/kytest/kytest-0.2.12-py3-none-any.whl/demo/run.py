"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest
from kytest.web import BrowserConfig

from data.login_data import get_headers


if __name__ == '__main__':
    # 不常用的浏览器参数设置
    BrowserConfig.headless = False

    hosts = {
        'api': 'https://app-test.qizhidao.com/',
        'web': 'https://www-test.qizhidao.com/'
    }
    kytest.main(
        pkg="com.qizhidao.clientapp",  # 应用包名，针对IOS、安卓、鸿蒙
        ability="EntryAbility",  # 页面名，针对鸿蒙，启动应用时使用
        host=hosts,  # 域名，针对接口和web测试
        headers=get_headers(),  # 请求头信息，针对接口测试
        path="tests/test_api.py",  # 测试脚本目录
        # xdist=True  # 并发执行，针对接口和web测试tests/Product_Detail_Controller
    )

