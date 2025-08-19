import shutil

from .executor import (
    _serial_execute,
    _parallel_execute
)
from .conf import App

from typing import Literal
from kytest.utils.log import logger
from kytest.utils.config import FileConfig
from dataclasses import dataclass


@dataclass
class ApiConfig:
    """
    接口测试配置类
    """
    host = None
    headers = None


@dataclass
class WebConfig:
    """
    web测试配置类
    """
    host = None
    headers = None
    browser: Literal["chrome", "firefox", "webkit", "msedge"] = 'chrome'
    headless: bool = False
    state_file_path: str = None
    maximized: bool = False
    window_size: list = None


@dataclass
class AppConfig:
    """
    APP测试配置类
    """
    did = None
    pkg = None
    ability = None
    wda_project_path = None
    run_mode = 'full'


@dataclass
class SonicConfig:
    """
    Sonic配置类
    """
    host = None
    user = None
    pwd = None
    sib_path = None


@dataclass
class OcrConfig:
    app_id = None
    api_key = None
    secret_key = None


class TestMain(object):
    """
    测试框架入口
    """

    def __init__(
            self,
            path: str = None,
            report: str = 'report',
            xdist: bool = False,
            rerun: int = 0,
            repeat: int = 0
    ):
        """
        @param path: 用例路径
        @param report: 报告路径
        @param xdist: 是否启用xdist插件，用于接口和web并发执行
        @param rerun: 失败重试次数
        @param repeat: 重复执行次数
        """
        logger.info("kytest start.")
        # 接口测试设置
        FileConfig.set_api('base_url', ApiConfig.host)
        FileConfig.set_api('headers', ApiConfig.headers)
        # web测试设置
        FileConfig.set_web('web_url', WebConfig.host)
        FileConfig.set_web('headers', WebConfig.headers)
        FileConfig.set_web('browser', WebConfig.browser)
        FileConfig.set_web('headless', WebConfig.headless)
        FileConfig.set_web('state', WebConfig.state_file_path)
        FileConfig.set_web('maximized', WebConfig.maximized)
        FileConfig.set_web('window_size', WebConfig.window_size)
        # OCR配置
        FileConfig.set_ocr('app_id', OcrConfig.app_id)
        FileConfig.set_ocr('api_key', OcrConfig.api_key)
        FileConfig.set_ocr('secret_key', OcrConfig.secret_key)
        # APP测试设置
        App.did = AppConfig.did
        App.pkg = AppConfig.pkg
        App.ability = AppConfig.ability
        App.wda_project_path = AppConfig.wda_project_path
        app_dict = {
            'did': App.did,
            'pkg': App.pkg,
            'ability': App.ability,
            'wda_project_path': App.wda_project_path
        }
        print(app_dict)
        # sonic设置
        App.sib_path = SonicConfig.sib_path
        App.sonic_host = SonicConfig.host
        App.sonic_user = SonicConfig.user
        App.sonic_pwd = SonicConfig.pwd
        sonic_dict = {
            'sib_path': App.sib_path,
            'host': App.sonic_host,
            'user': App.sonic_user,
            'pwd': App.sonic_pwd
        }
        print(sonic_dict)
        # 执行相关设置
        if not path:
            raise KeyError('测试用例路径不能为空')

        cmd_str = f'{path} -sv --alluredir {report} --clean-alluredir'
        if rerun:
            cmd_str += f' --reruns {str(rerun)}'
        if xdist:
            cmd_str += ' -n auto'
        if repeat:
            cmd_str += f' --count {repeat}'

        if isinstance(App.did, list):
            if not App.did:
                _serial_execute(path, cmd_str)
            elif len(App.did) == 1:
                App.did = App.did[0]
                _serial_execute(path, cmd_str)
            else:
                # 清空上次执行的目录
                shutil.rmtree(report, ignore_errors=True)
                # 多进程执行
                _parallel_execute(path, report, app_dict, sonic_dict)

        else:
            # 串行执行
            _serial_execute(path, cmd_str)

        # 文件参数重置
        FileConfig.reset()
        # App参数重置
        App.did = None
        App.pkg = None
        App.ability = None
        App.wda_project_path = None
        App.sib_path = None
        App.sonic_host = None
        App.sonic_user = None
        App.sonic_pwd = None


main = TestMain

if __name__ == '__main__':
    main()
