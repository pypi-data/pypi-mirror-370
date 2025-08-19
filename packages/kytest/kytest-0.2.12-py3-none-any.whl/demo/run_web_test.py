"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest
from kytest.web import BrowserConfig


if __name__ == '__main__':
    # 不常用的浏览器参数设置
    BrowserConfig.headless = False

    kytest.main(
        host='https://www-test.qizhidao.com/',  # 域名，针对接口和web测试
        path="test/test_web.py",  # 测试脚本目录
        # xdist=True  # 并发执行，针对接口和web测试tests/Product_Detail_Controller
    )

