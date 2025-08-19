"""
@Author: kang.yang
@Date: 2024/8/6 10:50
"""
import os
import sys
from . import __version__

login_content = '''import requests


def get_host_and_head(projectName: str, env: str = 'test'):
    """
    根据项目名获取登录态请求头
    :param env: 默认test
    :param projectName: qzd-bff-pcweb，目前只支持bff层的项目
    :return:
    """
    print("获取登录态数据")
    url = 'http://tmqa.qizhidao.net/api/common/getLoginHead'
    payload = {'projectName': projectName, "env": env}
    res = requests.get(url, params=payload)
    print(res.text)
    data = res.json()['data']
    host = data['host']
    head = data['headers']
    return host, head
'''


ignore_content = '''report
shot
.idea
.pytest_cache
__pycache__
debug.py
venv
generator.py
'''


api_run = '''import kytest
from data.login_data import get_host_and_head


if __name__ == '__main__':
    host, head = get_host_and_head('')
    kytest.main(
        host=host,
        headers=head,
        path='tests'
    )
'''

api_debug = '''import kytest
from data.login_data import get_host_and_head


if __name__ == '__main__':
    host, head = get_host_and_head('')
    kytest.main(
        host=host,
        headers=head,
        path='tests/test_demo.py'
    )
'''

web_recorder = '''from kytest.web import record_case


if __name__ == '__main__':
    url = "https://www.qizhidao.com/login"
    record_case(url)
'''

app_run = '''import kytest


if __name__ == '__main__':
    kytest.main(
        did='',
        pkg='',
        path='tests'
    )
'''

app_debug = '''import kytest


if __name__ == '__main__':
    kytest.main(
        did='',
        pkg='',
        path='tests/test_demo.py'
    )
'''

web_run = '''import kytest


if __name__ == '__main__':
    kytest.main(
        host={'web': 'xxx'},
        headers={},
        path='tests'
    )
'''

web_debug = '''import kytest


if __name__ == '__main__':
    kytest.main(
        host={'web': 'xxx'},
        headers={},
        path='tests/test_web.py'
    )
'''


def create_scaffold(platform):
    """create scaffold with specified project name."""

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    # 新增测试数据目录
    create_folder("tests")
    create_folder("data")
    create_file('.gitignore', ignore_content)
    # 新增安卓测试用例
    if platform in ("android", "ios", "hm"):
        create_folder("page")
        create_file('run_api.py', app_run)
        create_file('debug.py', app_debug)
        create_file('requirements.txt', f'kytest[{platform}]=={__version__}')
    elif platform == "web":
        create_folder("page")
        create_file('run_api.py', web_run)
        create_file('debug.py', web_debug)
        create_file('web_recorder.py', web_recorder)
        create_file('requirements.txt', f'kytest[{platform}]=={__version__}')
    elif platform == "api":
        create_file('run_api.py', api_run)
        create_file('debug.py', api_debug)
        create_file(os.path.join("data", "login_data.py"), login_content)
        create_file('requirements.txt', f'kytest=={__version__}')
    else:
        print("请输入正确的平台: android、ios、hm、web、api")
        sys.exit()
