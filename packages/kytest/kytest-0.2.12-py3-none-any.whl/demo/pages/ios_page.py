"""
@Author: kang.yang
@Date: 2023/11/16 17:36
"""
import kytest
from kytest.ios import Elem


class DemoPage(kytest.Page):
    adBtn = Elem(label='close white big')
    myTab = Elem(label='我的')
    setBtn = Elem(label='settings navi')
    about = Elem(text="关于企知道")
