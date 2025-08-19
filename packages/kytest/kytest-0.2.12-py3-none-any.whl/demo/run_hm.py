"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
from kytest import AppConfig, main


if __name__ == '__main__':
    AppConfig.did = 'xxx'
    AppConfig.pkg = 'com.qzd.hm'
    AppConfig.ability = 'EntryAbility'

    main(path="tests/test_hm.py")

