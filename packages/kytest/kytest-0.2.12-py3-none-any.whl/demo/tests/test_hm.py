"""
@Author: kang.yang
@Date: 2024/10/8 15:12
"""
from kytest.core.hm import TC
from page.hm_page import HmPage


class TestHmDemo(TC):

    def start(self):
        self.start_app()
        self.HP = HmPage(self.dr)

    def test_hm(self):
        self.dr.click(630, 2050)
        self.HP.my_entry.click()
        self.HP.login_entry.click()
        assert self.HP.pwd_login.exists()



