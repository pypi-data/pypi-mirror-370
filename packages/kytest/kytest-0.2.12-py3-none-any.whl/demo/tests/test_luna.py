"""
@Author: kang.yang
@Date: 2025/4/14 09:45
"""
from kytest.core.adr import AdrTC


class TestLunaMusic(AdrTC):
    """
    汽水音乐刷广告
    """

    def test_add(self):
        self.start_app(force=True)
        self.sleep(10)
        self.elem(resourceId='com.luna.music:id/kk').click_exists()
        self.sleep(10)
        while True:
            self.elem(resourceId='com.luna.music:id/kk').click_exists()
            self.sleep(10)
            self.dr.click(0.916, 0.065)
            self.elem(resourceId='com.luna.music:id/a7o').click_exists(timeout=1)
            self.elem(text='继续互动').click_exists(timeout=1)
            self.elem(text='继续观看').click_exists(timeout=1)
            self.elem(text='领取奖励').click_exists(timeout=1)






