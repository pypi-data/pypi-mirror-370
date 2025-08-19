import kytest
from page.adr_page import AdrPage


@kytest.story('测试demo')
class TestAdrDemo(kytest.AdrTC):
    def start(self):
        self.start_app()
        self.adr = AdrPage(self.dr)

    @kytest.title('进入设置页')
    def test_go_setting(self):
        if self.adr.ad_btn.exists():
            self.adr.ad_btn.click()
        self.adr.my_tab.click()
        self.adr.set_btn.click()
        self.adr.page_title.assert_text_eq('设置')





