"""
@Author: kang.yang
@Date: 2024/9/24 14:13
"""
# 需要启动tms服务
from kytest.api import generate_case


if __name__ == '__main__':
    host = "http://localhost:8001"
    project_name = 'kz-bff-patent'
    controller = 'Patent Controller'
    generate_case(host, project_name, controller)
