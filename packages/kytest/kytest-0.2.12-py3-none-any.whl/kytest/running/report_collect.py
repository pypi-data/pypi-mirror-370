"""
@Author: kang.yang
@Date: 2025/4/8 09:57
"""
import os
import json
import shutil

from kytest.utils.allure_util import AllureData


def _move_file(source_dir, target_dir):
    """
    测试结果文件归档
    @param source_dir:
    @param target_dir:
    @return:
    """
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
    """
    处理测试结果数据，以处理测试报告重复的问题
    @param device_id:
    @param report_path:
    @return:
    """
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
