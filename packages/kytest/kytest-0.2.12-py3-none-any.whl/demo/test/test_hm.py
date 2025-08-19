"""
@Author: kang.yang
@Date: 2024/10/8 15:12
"""
import kytest
from page.hm_page import HmPage


class TestHmDemo(kytest.HmTC):

    def start(self):
        self.start_app()
        self.hm = HmPage(self.dr)

    def test_hm(self):
        self.dr.click(630, 2050)
        self.hm.my_entry.click()
        self.hm.login_entry.click()
        assert self.hm.pwd_login.exists()



