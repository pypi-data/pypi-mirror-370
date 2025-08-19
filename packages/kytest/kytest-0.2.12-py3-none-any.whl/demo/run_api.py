"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
from kytest import ApiConfig, main
from data.login_data import get_headers


if __name__ == '__main__':
    ApiConfig.host = 'https://app-test.qizhidao.com/'
    ApiConfig.headers = get_headers()

    main(path="tests/test_api.py")



