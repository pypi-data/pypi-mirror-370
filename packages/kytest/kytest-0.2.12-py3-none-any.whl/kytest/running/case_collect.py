"""
@Author: kang.yang
@Date: 2025/4/8 09:56
"""
import os
import re
import subprocess

from .conf import App


def _get_case_list(path: str):
    """
    解析获取用例目录下的用例列表
    @param path:
    @return:
    """
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


def _collect_case_and_split(device_id, _path):
    """
    按传入设备列表把用例均分
    @param device_id:
    @param _path:
    @return:
    """
    _path_list = [{item: []} for item in device_id]
    test_cases = _get_case_list(_path)
    print(test_cases)
    # 把用例均分成设备数量的份数
    n = len(device_id)
    _lists = [[] for _ in range(n)]
    for _i, item in enumerate(test_cases):
        index = _i % n  # 计算元素应该分配给哪个列表
        _lists[index].append(item)
    return _lists


def _distribute_case_to_device(app_run_mode, path, report):
    """
    按执行模式把用例跟设备绑定
    @param app_run_mode:
    @param path:
    @param report:
    @return:
    """
    params = []
    if app_run_mode == 'split':
        lists = _collect_case_and_split(App.did, path)
        for i in range(len(App.did)):
            _path = lists[i][0] if len(lists[1]) < 2 else ','.join(lists[i])
            params.append((_path, App.did[i], App.pkg))
    else:
        for device in App.did:
            params.append((path, device, App.pkg, report, True))
    return params
