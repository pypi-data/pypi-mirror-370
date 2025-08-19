"""
@Author: kang.yang
@Date: 2023/11/16 17:50
"""
import kytest
from kytest.core.web import TC
from page.web_page import LoginPage


@kytest.story('登录')
class TestNormalSearch(TC):
    def start(self):
        self.LP = LoginPage(self.dr)

    @kytest.title("账号密码登录")
    def test_normal_search(self):
        self.LP.goto()
        self.LP.pwd_login.click()
        self.LP.phone_input.fill('13652435335')
        self.LP.pwd_input.fill('wz123456@QZD')
        self.LP.accept.click()
        self.LP.login_now.click()
        self.LP.first_company.click()
        self.sleep(10)






