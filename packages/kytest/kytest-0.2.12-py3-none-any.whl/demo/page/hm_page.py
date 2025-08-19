"""
@Author: kang.yang
@Date: 2024/10/8 15:04
"""
import kytest
from kytest.core.hm import Elem


class HmPage(kytest.Page):
    my_entry = Elem(text='我的')
    login_entry = Elem(text='登录/注册')
    pwd_login = Elem(text='账号登录')
    forget_pwd = Elem(text='忘记密码')

