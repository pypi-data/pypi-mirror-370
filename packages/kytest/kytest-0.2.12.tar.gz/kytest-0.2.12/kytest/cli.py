import click
from . import __version__
from .scaffold import create_scaffold


@click.group()
@click.version_option(version=__version__, help="Show version.")
# 老是变，等最后定下来再搞，目前也没啥用
def main():
    pass


# @main.command()
# @click.option('-p', '--platform', help="Specify the platform.")
# def create(platform):
#     """
#     创建新项目，老是变，先注释掉
#     @param platform: 平台，如api、android、ios、web
#     @return:
#     """
#     create_scaffold(platform)


# @main.command()
# @click.option('-p', '--platform', help="Specify the platform.")
# @click.option('-u', '--url', help="Specify the url.")
# def inspector(platform, url):
#     """
#     获取元素定位信息
#     @param platform: 平台，android、ios、web
#     @param url：针对web，需要录制的页面的url
#     @return:
#     """
#     import os
#     if platform in ['android', 'ios', 'web']:
#         os.system('weditor')
#     elif platform == 'web':
#         if not url:
#             raise KeyError('url不能为空')
#         os.system(f'playwright codegen {url}')
#     else:
#         raise KeyError('只支持android、ios、web')

