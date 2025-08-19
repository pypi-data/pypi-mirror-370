"""
@Author: kang.yang
@Date: 2023/11/16 17:49
"""
from kytest.core.web import Page, Elem


class IndexPage(Page):
    """首页"""
    url = "https://www-test.qizhidao.com/"
    loginBtn = Elem(xpath='(//div[text()="登录/注册"])[1]')
    patentText = Elem(xpath='//*[text()="查专利"]')


class LoginPage(Page):
    """登录页"""
    pwdTab = Elem(xpath='//*[text()="密码登录"]')
    userInput = Elem(xpath='//input[@placeholder="请输入手机号码"]')
    pwdInput = Elem(xpath='//input[@placeholder="请输入密码"]')
    accept = Elem(css=".agreeCheckbox .el-checkbox__inner")
    loginBtn = Elem(xpath='//*[text()="立即登录"]')
    firstItem = Elem(xpath="(//img[@class='right-icon'])[1]")


class LoginUtil:
    """登录模块公共方法"""

    def __init__(self, driver):
        self.ip = IndexPage(driver)
        self.lp = LoginPage(driver)

    def login(self, username='13652435335', password='wz123456@QZD'):
        """从首页进行登录"""
        self.ip.open()
        self.ip.sleep(5)
        self.ip.loginBtn.click()
        self.ip.sleep(5)
        self.lp.pwdTab.click()
        self.lp.userInput.input(username)
        self.lp.pwdInput.input(password)
        self.lp.accept.click()
        self.lp.loginBtn.click()
        self.lp.firstItem.click()

