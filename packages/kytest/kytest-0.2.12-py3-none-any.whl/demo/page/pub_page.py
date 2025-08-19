"""
@Author: kang.yang
@Date: 2024/9/23 15:23
"""
from page.web_page import LoginPage
from data.user_data import USERNAME, PASSWORD


# 公共方法放在这个公共方法中
class PubPage:
    """登录模块公共方法"""

    def __init__(self, driver):
        self.lp = LoginPage(driver)

    def login(self, username=USERNAME, password=PASSWORD):
        """从首页进行登录"""
        self.lp.goto()
        self.lp.login_or_reg.click()
        self.lp.pwd_login.click()
        self.lp.phone_input.fill(username)
        self.lp.pwd_input.fill(password)
        self.lp.accept.click()
        self.lp.login_now.click()
        self.lp.first_company.click()

