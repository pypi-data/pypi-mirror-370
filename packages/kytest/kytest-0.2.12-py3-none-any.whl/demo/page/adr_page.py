"""
@Author: kang.yang
@Date: 2024/9/14 09:44
"""
import kytest
from kytest.core.adr import Elem


class AdrPage(kytest.Page):
    ad_btn = Elem(rid='id/bottom_btn')
    my_tab = Elem(xpath='//android.widget.FrameLayout[4]')
    space_tab = Elem(text='科创空间')
    set_btn = Elem(rid='id/me_top_bar_setting_iv')
    title = Elem(rid='id/tv_actionbar_title')
    agree_text = Elem(rid='id/agreement_tv_2')
    page_title = Elem(rid='id/tv_actionbar_title')

