"""
@Author: kang.yang
@Date: 2023/8/1 18:21
"""
import random
import socket
import time
import os


def general_file_path(file_name):
    if not file_name:
        raise ValueError("文件名不能为空")

    # 截图并保存到当前目录的image文件夹中
    relative_path = "shots"
    # 把文件名处理成test.png的样式
    if "." in file_name:
        file_name = file_name.split(r".")[0]
    if os.path.exists(relative_path) is False:
        os.mkdir(relative_path)

    time_str = time.strftime(f"%Y%m%d%H%M%S")
    file_name = f"{time_str}_{file_name}.jpg"
    file_path = os.path.join(relative_path, file_name)
    return file_path


def is_port_in_use(port: int) -> bool:
    """判断端口是否已占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def get_free_port():
    """获取空闲端口"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        try:
            return s.getsockname()[1]
        finally:
            s.close()
    except OSError:
        # bind 0 will fail on Manjaro, fallback to random port
        # https://github.com/openatx/adbutils/issues/85
        for _ in range(20):
            port = random.randint(10000, 20000)
            if not is_port_in_use(port):
                return port
        raise RuntimeError("No free port found")


