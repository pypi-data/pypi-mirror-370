"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
from kytest import AppConfig, main


if __name__ == '__main__':
    AppConfig.did = ['417ff34c']
    AppConfig.pkg = 'com.qizhidao.clientapp'
    AppConfig.run_mode = 'polling'

    main(path="tests/test_adr.py")



