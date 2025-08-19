"""
@Author: kang.yang
@Date: 2024/4/29 09:31
"""
import os
import re
import shutil
import subprocess
import pytest
import json

from kytest.running.conf import App
from kytest.utils.log import logger
from kytest.utils.allure_util import AllureData


def _get_case_list(path: str):
    # 获取所有用例文件的完整路径列表
    _total_file_list = []
    for root, dirs, files in os.walk(path):
        if 'pycache' in root:
            continue
        files_str = ''.join(files)
        if '.py' not in files_str:
            continue
        files = [item for item in files if item != '__init__.py']
        if files:
            for _file in files:
                _total_file_list.append(os.path.join(root, _file))

    # 获取path目录下的用例原始字符串
    cases_str = subprocess.run(['pytest', path, '--collect-only'], capture_output=True, text=True).stdout

    # 把所有的标签拿出来
    lines = cases_str.split("\n")
    result = []

    for line in lines:
        match = re.search(r"<(.*?)>", line)
        if match:
            item = match.group(1)
            result.append(item)

    # 解析成用例列表
    case_list = []
    current_package = ''
    current_module = ''
    current_class = ''
    for item in result:
        if 'Package' in item:
            current_package = item.split(" ")[1]
        if 'Module' in item:
            current_module = item.split(" ")[1]
        if 'Class' in item:
            current_class = item.split(" ")[1]
        if 'Function' in item:
            _function = item.split(" ")[1].split("[")[0]
            _file_path = f"{current_package}/{current_module}"
            for item in _total_file_list:
                if _file_path in item:
                    _file_path = item
                    break
            print(f"{_file_path}::{current_class}::{_function}")
            case_list.append(f"{_file_path}::{current_class}::{_function}")

    # 去重
    print("去重后：")
    case_list = sorted(list(set(case_list)))
    for case in case_list:
        print(case)

    return case_list


def _move_file(source_dir, target_dir):
    # 获取源目录中的所有文件名列表
    file_list = os.listdir(source_dir)

    for file in file_list:
        # 构建源文件的完整路径
        source_file = os.path.join(source_dir, file)

        if not os.path.isdir(source_file):  # 判断是否为文件而非子目录
            # 构建目标文件的完整路径
            target_file = os.path.join(target_dir, file)

            try:
                # 移动文件至目标目录
                shutil.move(source_file, target_file)

                print('已移动文件：', file)
            except Exception as e:
                print('移动文件时发生错误：', str(e))


def _change_name_and_historyId(device_id, report_path):
    _allure = AllureData(result_path=report_path)
    result_list = _allure.get_files()
    for result in result_list:
        content = _allure.get_file_content(result)
        # 获取name，给name带上-{serial}的后缀
        content["name"] = content["name"] + "-" + device_id
        # 获取historyId，在后面带上-{serial}的后缀
        content["historyId"] = content["historyId"] + "-" + device_id
        # content重新写入回result中
        with open(result, "w") as f:
            f.write(json.dumps(content))


def _app_main(path, did, pkg, report_path, is_all=False):
    # 修改配置
    # App.serial = serial
    # App.package = package
    # App.udid = udid
    # App.bundle_id = bundle_id
    # App.ocr_service = ocr_api
    # App.auto_start = start
    App.did = did
    App.pkg = pkg

    # 执行用例
    # 由于是多设备并发执行，所以要对报告目录进行区分，后面增加合并的能力(有空调研一下pytest-xdist的报告合并实现方式)
    if is_all is True:
        if did:
            report_path = f"report-{did}"
            cmd_list = [path, '-sv', '--alluredir', report_path]
            logger.info(cmd_list)
            pytest.main(cmd_list)
            # 进行合并，修改result.json中的name和historyId
            _change_name_and_historyId(did, report_path)

            # 把目录中的文件都移入report目录中
            if not os.path.exists('report'):
                os.makedirs('report')
            _move_file(report_path, 'report')

            # 删除原目录
            shutil.rmtree(report_path, ignore_errors=True)
        # if udid:
        #     report_path = f"report-{udid}"
        #     cmd_list = [path, '-sv', '--alluredir', report_path]
        #     logger.info(cmd_list)
        #     pytest.main(cmd_list)
        #     # 进行合并
        #     _change_name_and_historyId(udid, report_path)
        #
        #     # 把目录中的文件都移入report目录中
        #     if not os.path.exists('report'):
        #         os.makedirs('report')
        #     _move_file(report_path, 'report')
        #
        #     # 删除原目录
        #     shutil.rmtree(report_path, ignore_errors=True)
    else:
        cmd_list = [path, '-sv', '--alluredir', report_path]
        logger.info(cmd_list)
        pytest.main(cmd_list)
