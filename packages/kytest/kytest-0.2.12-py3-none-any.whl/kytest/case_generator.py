"""
@Author: kang.yang
@Date: 2024/8/24 09:24
"""
import sys
import os
import requests
from urllib.parse import urljoin
from .utils.nacos_util import knacos


def generate_case(project: str, controller: str, base_path: str = 'tests'):
    """
    生成用例
    @param project: tms服务导入的项目
    @param controller: 指定的controller，不指定则生成全部
    @param base_path：指定生成的目录，默认当前目录
    @return:
    """
    host = knacos.get_by_data_id("TMS_HOST")

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    if not host:
        print('host不能为空')
        sys.exit()
    if not project:
        print('project不能为空')
        sys.exit()

    url = urljoin(host, '/api/api_test/api/get_apis_by_project_and_controller')
    query = {
        "project_name": project,
        "controller": controller
    }
    try:
        res = requests.get(url, params=query).json()
    except requests.exceptions.ConnectionError:
        print(f"{host}服务连接异常，请去nacos确认TMS_HOST配置正确~")
        sys.exit()
    if res["code"] == 0:
        api_list = res["data"]
        # 生成用例
        for api in api_list:
            controller = api["controller"]
            if base_path is not None:
                controller_path = os.path.join(base_path, controller)
            else:
                controller_path = controller
            if not os.path.exists(controller_path):
                create_folder(controller_path)
            test_name = api["test_name"]
            print(f"生成用例: {test_name}")
            test_script = api["test_script"]
            create_file(os.path.join(controller_path, test_name), test_script)
        print(f"共生成{len(api_list)}条用例.")
    else:
        print("用例生成异常")
        print(res)
        sys.exit()
