"""
@Author: kang.yang
@Date: 2024/9/24 09:11
"""
import subprocess
import time
import os


page_start = '''import kytest


class RecordPage(kytest.Page):'''

case_start = '''import kytest

from page.record_page import RecordPage


@kytest.story('录制模块')
class TestRecord(kytest.WebTC):
    def start(self):
        self.rp = RecordPage(self.dr)

    @kytest.title("录制场景")
    def test_record(self):'''


def create_folder(path):
    os.makedirs(path)
    msg = f"created folder: {path}"
    print(msg)


def create_file(path, file_content=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(file_content)
    msg = f"created file: {path}"
    print(msg)


def record_case(url):
    """
    使用playwright codegen录制脚本并转换成page和test
    @param url:
    @return:
    """
    # 启动 playwright codegen 命令，保持非阻塞模式
    process = subprocess.Popen(['playwright',
                                'codegen',
                                url,
                                '-o',
                                'recorded.py'
                                ])

    while True:
        # 每秒钟检查一次进程状态
        return_code = process.poll()
        # return_code = 0

        # 打印 returncode，如果进程还未结束，returncode 会是 None
        print(f'Return code: {return_code}')

        if return_code == 0:
            with open('recorded.py', 'r') as f:
                scripts = f.readlines()
            page_content = page_start
            case_content = case_start
            for i, script in enumerate(scripts):
                script = script.strip()
                # 其它的特殊场景暂时先不管
                if script.startswith('page.') and 'page.close' not in script:
                    # 解析
                    if 'goto' in script:
                        url = script.split('"')[-2]
                        page_content += f'\n    url_{i} = "{url}"'
                        case_content += f'\n        self.rp.goto(self.rp.url_{i})'
                    else:
                        loc, operation = script.rsplit('.', 1)
                        loc = loc[4:]
                        elem_name = f'elem_{i}'
                        page_content += f'\n    {elem_name} = kytest.WebElem(){loc}'
                        case_content += f'\n        self.rp.{elem_name}.{operation}'

            # 生成page：page/record_page.py => RecordPage
            # 如果没有page目录，新建一个
            if not os.path.exists('page'):
                create_folder('page')
            create_file(os.path.join('page', 'record_page.py'), page_content + '\n')
            # 生成test：tests/test_record.py => TestRecord
            if not os.path.exists('tests'):
                create_folder('tests')
            create_file(os.path.join('tests', 'test_record.py'), case_content + '\n')

            break

        # 等待 1 秒再进行下一次检查
        time.sleep(1)

    # 如果进程仍然在运行，在这里等待它完全结束
    process.wait()



