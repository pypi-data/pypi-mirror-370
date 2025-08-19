"""
@Author: kang.yang
@Date: 2023/5/12 20:49
"""
import allure
import os

from typing import Literal
from playwright.sync_api import sync_playwright, expect

from kytest.utils.log import logger
from kytest.utils.common import general_file_path


class Browser:
    """
    用于浏览器的安装
    """

    def __init__(self,
                 browserName:
                 Literal[
                     "chrome",
                     "firefox",
                     "webkit",
                     "msedge",
                 ] = None):
        self.browserName = browserName

    def install(self):
        if self.browserName is None:
            logger.info('安装所有浏览器')
            os.system('playwright install')
        else:
            logger.info(f'安装{self.browserName}浏览器')
            os.system(f'playwright install {self.browserName}')


class Driver:
    """
    用于浏览器的操作
    https://playwright.dev/python/docs/locators
    """

    def __init__(
            self,
            browserName: Literal[
                "chrome",
                "firefox",
                "webkit",
                "msedge"] = "chrome",
            headless: bool = False,
            state: str = None,
            maximized: bool = False,
            window_size: list = None
    ):
        """
        浏览器驱动
        @param browserName: 浏览器类型，默认chrome，还支持firefox和webkit
        @param headless: 是否使用无头模式
        @param state: 使用state.json加载登录态
        @param maximized: 是否使用全屏模式
        @param window_size: 指定窗口分辨率，如[1920, 1080]
        """
        # browName判断
        support_browser_list = [
            "chromium",
            "chrome",
            "chrome-beta",
            "msedge",
            "msdege-beta",
            "medege-dev",
            "firefox",
            "webkit"
        ]
        if browserName not in support_browser_list:
            raise KeyError(f"不支持的浏览器类型: {browserName}")

        logger.info("浏览器驱动初始化")
        if headless is True and window_size is None:
            window_size = [1920, 1080]

        self.playwright = sync_playwright().start()
        _kwargs = {"headless": headless}
        if maximized and window_size is None:
            _kwargs["args"] = ['--start-maximized']
        if browserName == 'firefox':
            self.browser = self.playwright.firefox.launch(**_kwargs)
        elif browserName == 'webkit':
            self.browser = self.playwright.webkit.launch(**_kwargs)
        elif 'msedge' in browserName:
            _kwargs["channel"] = 'msedge'
            self.browser = self.playwright.chromium.launch(**_kwargs)
        else:
            self.browser = self.playwright.chromium.launch(**_kwargs)

        _context_kwargs = {"storage_state": state}
        if maximized and window_size is None:
            _context_kwargs["no_viewport"] = True
        if window_size:
            _context_kwargs["viewport"] = {'width': window_size[0], 'height': window_size[1]}
        self.context = self.browser.new_context(**_context_kwargs)
        self.page = self.context.new_page()

    def dialog_handler(self, _type: str = "dismiss"):
        """
        监听dialog，默认取消或者同意
        @param _type:
        @return:
        """
        if _type == "dismiss":
            self.page.on("dialog", lambda dialog: dialog.dismiss())
        else:
            self.page.on("dialog", lambda dialog: dialog.accept())

    def goto(self, url):
        logger.info(f"访问页面: {url}")
        self.page.goto(url)

    def storage_state(self, path=None):
        logger.info("保存浏览器状态信息")
        if not path:
            raise ValueError("路径不能为空")
        self.context.storage_state(path=path)

    @property
    def page_content(self):
        """获取页面内容"""
        logger.info("获取页面内容")
        content = self.page.content()
        logger.info(content)
        return content

    def add_cookies(self, cookies: list):
        logger.info("添加cookie并刷新页面")
        self.context.add_cookies(cookies)
        self.page.reload()

    def shot(self, file_name=None):
        file_path = general_file_path(file_name)
        logger.info(f"保存至: {file_path}")
        self.page.screenshot(path=file_path)
        logger.info("截图上传allure报告")
        allure.attach.file(
            file_path,
            attachment_type=allure.attachment_type.PNG,
            name=f"{file_path}",
        )
        return file_path

    def press(self, key):
        logger.info("键盘点击")
        self.page.keyboard.press(key)

    def back(self):
        logger.info("返回上一页")
        self.page.go_back()

    def close(self):
        logger.info("关闭浏览器")
        self.page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def assert_title(self, title: str, timeout: int = 5):
        logger.info(f"断言页面标题等于: {title}")
        expect(self.page).to_have_title(title,
                                        timeout=timeout * 1000)

    def assert_url(self, url: str, timeout: int = 5):
        logger.info(f"断言页面url等于: {url}")
        expect(self.page).to_have_url(url,
                                      timeout=timeout * 1000)


if __name__ == '__main__':
    pass
