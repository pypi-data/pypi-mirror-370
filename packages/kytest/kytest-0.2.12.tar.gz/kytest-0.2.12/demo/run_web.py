"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
from kytest import WebConfig, main


if __name__ == '__main__':
    WebConfig.host = 'https://www.qizhidao.com/'
    WebConfig.browser = 'chrome'

    main(path="tests/test_web.py")


