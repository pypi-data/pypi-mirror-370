"""
@Author: kang.yang
@Date: 2023/11/16 17:36
"""
import kytest
from kytest.ios import Elem
from kytest.img import ImgElem


class ImagePage(kytest.Page):
    searchBtn = Elem(text="搜索", className="XCUIElementTypeSearchField")
    searchInput = Elem(className="XCUIElementTypeSearchField")
    searchResult = Elem(xpath="//Table/Cell[2]")
    schoolEntry = ImgElem(file="../data/校园场馆.png")
