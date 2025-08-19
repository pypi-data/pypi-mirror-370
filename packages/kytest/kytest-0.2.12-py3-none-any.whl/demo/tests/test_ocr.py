"""
@Author: kang.yang
@Date: 2023/11/16 17:48
"""
import kytest

from pages.image_page import OcrPage


class TestOcrDemo(kytest.TestCase):
    """ocr识别demo"""

    def start(self):
        self.op = OcrPage(self.driver)

    def test_nanshan_wtt(self):
        self.op.searchBtn.click()
        self.op.searchInput.input("南山文体通")
        self.op.searchResult.click()
        self.op.schoolEntry.click()
        self.sleep(5)


if __name__ == '__main__':
    kytest.main(
        plat='ios',
        device_id='00008101-000E646A3C29003A',
        pkg_name='com.tencent.xin'
    )
