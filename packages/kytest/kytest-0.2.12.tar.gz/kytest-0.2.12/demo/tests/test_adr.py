import kytest
from kytest.core.adr import TC
from page.adr_page import AdrPage


@kytest.story('测试demo')
class TestAdrDemo(TC):
    def start(self):
        self.start_app()
        self.AP = AdrPage(self.dr)

    def end(self):
        self.stop_app()

    @kytest.title('进入我的页')
    def test_switch_to_my(self):
        if self.AP.ad_btn.exists():
            self.AP.ad_btn.click()
        self.AP.my_tab.click()
        self.sleep(5)

    @kytest.title('进入科创空间')
    def test_switch_to_space(self):
        if self.AP.ad_btn.exists():
            self.AP.ad_btn.click()
        self.AP.space_tab.click()
        self.sleep(5)







