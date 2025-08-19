"""
@Author: kang.yang
@Date: 2023/11/16 17:48
"""
from kytest.ios import TestCase

from pages.image_page import ImagePage


class TestImageDemo(TestCase):
    """ocr识别demo"""

    def start(self):
        self.keyword = "南山文体通"
        self.page = ImagePage(self.driver)

    def test_nanshan_wtt(self):
        self.page.searchBtn.click()
        self.page.searchInput.\
            input(self.keyword)
        self.page.searchResult.click()
        self.page.schoolEntry.click()
        self.sleep(5)

