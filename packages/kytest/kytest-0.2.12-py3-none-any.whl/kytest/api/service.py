"""
@Author: kang.yang
@Date: 2024/8/24 09:24
"""
import sys
import os
import requests
from urllib.parse import urljoin
from kytest.utils.allure_util import AllureData


def generate_case(host: str, project: str, controller: str, base_path: str = 'tests'):
    """
    生成用例
    @param host: tms服务的域名
    @param project: tms服务导入的项目
    @param controller: 指定的controller，不指定则生成全部
    @param base_path：指定生成的目录，默认当前目录
    @return:
    """

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
        print(f"{host}服务连接异常~")
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


def check_coverage_data(backend_url, project_name):
    """
    检查接口平台已覆盖的接口在脚本中是否都已覆盖
    @param backend_url: tms平台后端服务域名，如: http://localhost:8001
    @param project_name: tms平台已导入接口项目名，如：kz-bff-patent
    @return:
    """
    apis_covered = AllureData().get_api_list()
    url = f"{backend_url}/api/api_test/api/check_test_result"
    body = {
        "project_name": project_name,
        "apis_covered": apis_covered
    }
    res = requests.post(url, json=body)

    if res.json()['data']['status'] == 'pass':
        print("都已真实覆盖。")
    else:
        miss_list = res.json()['data']['error_list']
        print(f"还有{len(miss_list)}个接口漏掉了，如下：")
        for api in miss_list:
            print(api)
