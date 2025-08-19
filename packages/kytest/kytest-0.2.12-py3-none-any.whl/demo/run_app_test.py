"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest


if __name__ == '__main__':
    kytest.main(
        pkg="com.qizhidao.clientapp",  # 应用包名，针对IOS、安卓、鸿蒙
        ability="EntryAbility",  # 页面名，针对鸿蒙，启动应用时使用
        path="test/test_adr.py",  # 测试脚本目录
    )

