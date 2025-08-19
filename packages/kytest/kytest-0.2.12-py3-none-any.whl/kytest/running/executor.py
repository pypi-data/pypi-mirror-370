"""
@Author: kang.yang
@Date: 2024/4/29 09:31
"""
import os
import shutil
import pytest

from .report_collect import _change_name_and_historyId, _move_file
from .case_collect import _get_case_list

import queue
from multiprocessing import Process, Queue, Lock
from kytest.running.conf import App
from kytest.utils.log import logger


def _app_main(path, did, pkg, report_path, wda_project_path, sib_path, sonic_host, sonic_user, sonic_pwd):
    """
    根据分配好的用例和设备数据，进行执行（本地设备）
    @param path:
    @param did:
    @param pkg:
    @param report_path:
    @return:
    """
    if not did:
        return

    App.did = did
    App.pkg = pkg
    App.wda_project_path = wda_project_path
    App.sib_path = sib_path
    App.sonic_host = sonic_host
    App.sonic_user = sonic_user
    App.sonic_pwd = sonic_pwd

    # 执行用例
    _report_path = f"report-{did}"
    cmd_list = [path, '-sv', '--alluredir', _report_path]
    logger.info(cmd_list)
    pytest.main(cmd_list)
    # 进行合并，修改result.json中的name和historyId
    _change_name_and_historyId(did, _report_path)

    # 把目录中的文件都移入report目录中
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    _move_file(_report_path, report_path)

    # 删除原目录
    shutil.rmtree(_report_path, ignore_errors=True)


def _app_main_polling(queue1: Queue, lock: Lock, did, pkg, report_path, wda_project_path, sib_path, sonic_host, sonic_user, sonic_pwd):
    """
    根据分配好的用例和设备数据，进行执行（本地设备）
    @param queue1
    @param lock
    @param did:
    @param pkg:
    @param report_path:
    @return:
    """
    if not did:
        return

    while True:
        try:
            case = queue1.get(timeout=1)
            print(f"设备{did}正在执行用例{case}")
            App.did = did
            App.pkg = pkg
            App.wda_project_path = wda_project_path
            App.sib_path = sib_path
            App.sonic_host = sonic_host
            App.sonic_user = sonic_user
            App.sonic_pwd = sonic_pwd

            # 执行用例
            _report_path = f"report-{did}"
            cmd_list = [case, '-sv', '--alluredir', _report_path]
            logger.info(cmd_list)
            pytest.main(cmd_list)
            # 进行合并，修改result.json中的name和historyId
            _change_name_and_historyId(did, _report_path)

            # 把目录中的文件都移入report目录中
            if not os.path.exists(report_path):
                os.makedirs(report_path)
            _move_file(_report_path, report_path)

            # 删除原目录
            shutil.rmtree(_report_path, ignore_errors=True)

            # 加锁
            with lock:
                with open("output.txt", "a") as f:
                    f.write(f"设备{did}的用例{case}执行完成")
            print(f"设备{did}的用例{case}执行完成")
        except queue.Empty:
            break


def _serial_execute(_path, cmd_str):
    """
    串行执行
    @param _path:
    @param cmd_str:
    @return:
    """
    cmd_list = cmd_str.split()
    pytest.main(cmd_list)


def _parallel_execute(path, report, app: dict, sonic: dict):
    devices = app.get('did', None)
    pkg = app.get('pkg', None)
    app_run_mode = app.get('run_mode', None)
    wda_project_path = app.get('wda_project_path', None)
    sib_path = sonic.get('sib_path', None)
    sonic_host = sonic.get('host', None)
    sonic_user = sonic.get('user', None)
    sonic_pwd = sonic.get('pwd', None)

    # 设备并发
    if app_run_mode == 'polling':
        # 轮询执行部分用例，设备并发启动
        # 收集测试用例
        case_list = _get_case_list(path)
        # 把测试用例存进队列
        queue1 = Queue()
        lock = Lock()
        for case in case_list:
            queue1.put(case)
        # 每个设备开启一个进程，从队列里面拿用例执行，直到用例执行完
        processes = []
        for device in devices:
            params = (queue1, lock, device, pkg, report, wda_project_path, sib_path, sonic_host, sonic_user, sonic_pwd)
            p = Process(target=_app_main_polling, args=params)
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
    else:
        # 执行全部用例，设备并发启动
        processes = []
        for device in devices:
            param = (path, device, pkg, report, wda_project_path, sib_path, sonic_host, sonic_user, sonic_pwd)
            pr = Process(target=_app_main, args=param)
            pr.start()
            processes.append(pr)
        for p in processes:
            p.join()
    print("所有用例执行完毕")






