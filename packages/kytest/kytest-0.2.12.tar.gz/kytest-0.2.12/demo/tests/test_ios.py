"""
@Author: kang.yang
@Date: 2025/4/11 16:16
"""
from kytest.core.ios import TC
from page.ios_page import IosPage


class TestIosDemo(TC):

    def start(self):
        self.start_app()
        self.sleep(5)
        self.IP = IosPage(self.dr)

    def end(self):
        self.stop_app()

    def test_switch_to_lg(self):
        self.IP.music_tab.click()
        self.sleep(5)

    def test_switch_to_jb(self):
        self.IP.gold_tab.click()
        self.sleep(5)
