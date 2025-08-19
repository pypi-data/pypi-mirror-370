"""
@Author: kang.yang
@Date: 2023/5/13 10:16
"""
from playwright.sync_api import expect, Locator

from kytest.web.driver import Driver

from kytest.utils.log import logger


# 链式调用临时存储定位方式
class RoleLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'role'


class TextLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'text'


class LabelLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'label'


class PlaceholderLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'placeholder'


class AltTextLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'alt_text'


class TitleLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'title'


class TestIdLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'test_id'


class FrameLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'frame'


class LocatorLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'locator'


class FilterLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'filter'


class NthLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'nth'


class FirstLocator:

    def __init__(self):
        self.type = 'first'


class LastLocator:

    def __init__(self):
        self.type = 'last'


class Elem:
    """
    通过playwright定位的web元素
    https://playwright.dev/python/docs/locators
    """

    def __init__(self,
                 driver: Driver = None,
                 role=None,
                 name=None,
                 text=None,
                 label=None,
                 placeholder=None,
                 alt_text=None,
                 title=None,
                 test_id=None,
                 frame_loc=None,
                 locator=None,
                 exact=False,
                 watch=False
                 ):

        self._driver = driver
        self._kwargs = {}

        self.role = role
        if self.role:
            self._kwargs['role'] = role
        self.name = name
        if self.name:
            self._kwargs['name'] = name
        self.text = text
        if self.text:
            self._kwargs['text'] = text
        self.label = label
        if self.label:
            self._kwargs['label'] = label
        self.placeholder = placeholder
        if self.placeholder:
            self._kwargs['placeholder'] = placeholder
        self.alt_text = alt_text
        if self.alt_text:
            self._kwargs['alt_text'] = alt_text
        self.title = title
        if self.title:
            self._kwargs['title'] = title
        self.test_id = test_id
        if self.test_id:
            self._kwargs['test_id'] = test_id
        self.frame_loc = frame_loc
        if self.frame_loc:
            self._kwargs['frame_loc'] = frame_loc
        self.loc = locator
        if self.loc:
            self._kwargs['locator'] = locator
        self.exact = exact
        if self.exact:
            self._kwargs['exact'] = exact
        self.locators = []
        self._watch = watch

    def __call__(self, *args, **kwargs):
        return self

    def __get__(self, instance, owner):
        """pm模式的关键"""
        if instance is None:
            return None
        self._driver = instance.driver
        return self

    # 链式调用方法
    def get_by_role(self, *args, **kwargs):
        self.locators.append(RoleLocator(*args, **kwargs))
        return self

    def get_by_text(self, *args, **kwargs):
        self.locators.append(TextLocator(*args, **kwargs))
        return self

    def get_by_label(self, *args, **kwargs):
        self.locators.append(LabelLocator(*args, **kwargs))
        return self

    def get_by_placeholder(self, *args, **kwargs):
        self.locators.append(PlaceholderLocator(*args, **kwargs))
        return self

    def get_by_alt_text(self, *args, **kwargs):
        self.locators.append(AltTextLocator(*args, **kwargs))
        return self

    def get_by_title(self, *args, **kwargs):
        self.locators.append(TitleLocator(*args, **kwargs))
        return self

    def get_by_test_id(self, *args, **kwargs):
        self.locators.append(TestIdLocator(*args, **kwargs))
        return self

    def frame_locator(self, *args, **kwargs):
        self.locators.append(FrameLocator(*args, **kwargs))
        return self

    def locator(self, *args, **kwargs):
        self.locators.append(LocatorLocator(*args, **kwargs))
        return self

    def filter(self, *args, **kwargs):
        self.locators.append(FilterLocator(*args, **kwargs))
        return self

    def nth(self, *args, **kwargs):
        self.locators.append(NthLocator(*args, **kwargs))
        return self

    @property
    def first(self):
        self.locators.append(FirstLocator())
        return self

    @property
    def last(self):
        self.locators.append(LastLocator())
        return self

    def get_first_locator(self):
        logger.info(f"第一定位: {self._kwargs}")
        if self.role is not None:
            if self.name is not None:
                return self._driver.page.get_by_role(self.role, name=self.name)
            else:
                return self._driver.page.get_by_role(self.role)
        elif self.text is not None:
            if self.exact is True:
                return self._driver.page.get_by_text(self.text, exact=True)
            else:
                return self._driver.page.get_by_text(self.text)
        elif self.label is not None:
            return self._driver.page.get_by_label(self.label)
        elif self.placeholder is not None:
            return self._driver.page.get_by_placeholder(self.placeholder)
        elif self.alt_text is not None:
            return self._driver.page.get_by_alt_text(self.alt_text)
        elif self.title is not None:
            return self._driver.page.get_by_title(self.title)
        elif self.test_id is not None:
            return self._driver.page.get_by_test_id(self.test_id)
        elif self.frame_loc is not None:
            return self._driver.page.frame_locator(self.frame_loc)
        elif self.loc is not None:
            return self._driver.page.locator(self.loc)
        else:
            logger.info("第一个元素为空")
            return self._driver.page

    def find(self, timeout=5, n=3):
        """查找指定的一个元素"""
        logger.info(f"查找元素")
        element = self.get_first_locator()
        # 链式调用方法叠加
        if self.locators:
            logger.info(f"链式调用: {self.locators}")
            for loc_obj in self.locators:
                if loc_obj.type == "role":
                    element = element.get_by_role(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'text':
                    element = element.get_by_text(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'label':
                    element = element.get_by_label(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'placeholder':
                    element = element.get_by_placeholder(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'alt_text':
                    element = element.get_by_alt_text(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'title':
                    element = element.get_by_title(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'test_id':
                    element = element.get_by_test_id(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'frame':
                    element = element.frame_locator(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'locator':
                    element = element.locator(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'filter':
                    element = element.filter(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'nth':
                    element = element.nth(*loc_obj.args, **loc_obj.kwargs)
                elif loc_obj.type == 'first':
                    element = element.first
                elif loc_obj.type == 'last':
                    element = element.last

        try:
            element.wait_for(timeout=timeout * 1000)
            return element
        except:
            retry_count = n
            if retry_count > 0:
                for count in range(1, retry_count + 1):
                    logger.info(f"第{count}次重试...")
                    if self._watch:
                        self._driver.dialog_handler()
                    try:
                        element.wait_for(timeout=timeout * 1000)
                        # if self._debug is True:
                        #     element.evaluate('(element) => element.style.border = "2px solid red"')
                        #     time.sleep(1)
                        #     self._driver.shot("查找成功")
                        return element
                    except:
                        continue

            self._driver.shot("查找失败")
            raise Exception("查找失败")

    # 属性
    def is_visible(self, timeout=1):
        logger.info("是否可见")
        return self.find(timeout=timeout, n=0).is_visible()

    def is_hidden(self, timeout=1):
        logger.info("是否隐藏")
        return self.find(timeout=timeout, n=0).is_hidden()

    def text_content(self):
        logger.info("获取文本")
        elem = self.find()
        text = elem.text_content()
        logger.info(text)
        return text

    def all_text_content(self):
        logger.info("获取多个文本")
        elems = self.find().all()
        text_list = [elem.text_content() for elem in elems]
        logger.info(text_list)
        return text_list

    # 操作
    def click(self, timeout=5, *args, **kwargs):
        """
        page.get_by_text("Item").click(button="right")
        page.get_by_text("Item").click(modifiers=["Shift"])
        page.get_by_text("Item").click(position={ "x": 0, "y": 0})
        page.get_by_role("button").click(force=True)
        @param timeout: 
        @param args: 
        @param kwargs: 
        @return: 
        """
        logger.info("点击")
        self.find(timeout=timeout).click(*args, **kwargs)
        logger.info("点击完成")

    def dispatch_event_click(self, timeout=5):
        """
        其它点击方式都不管用了可以试试这个
        @param timeout:
        @return:
        """
        logger.info("js事件点击")
        self.find(timeout=timeout).dispatch_event('click')
        logger.info("点击完成")

    def dbclick(self, timeout=5):
        logger.info("双击")
        self.find(timeout=timeout).dblclick()
        logger.info("双击完成")

    def fill(self, text, timeout=5):
        logger.info(f"输入: {text}")
        self.find(timeout=timeout).fill(text)
        logger.info("输入完成")

    def press(self, key, timeout=5):
        """
        @param key: 单个键位支持Backquote, Minus, Equal, Backslash, Backspace, Tab, Delete, Escape,
        ArrowDown, End, Enter, Home, Insert, PageDown, PageUp, ArrowRight, ArrowUp, F1 - F12, Digit0 - Digit9,
        KeyA - KeyZ, etc.
                    还支持组合键，如Shift+A、Control+o、Control+Shift+T
        @param timeout:
        @return:
        """
        logger.info(f"键盘点击")
        self.find(timeout=timeout).press(key)
        logger.info("点击完成")

    def press_sequentially(self, words: str, timeout=5):
        """
        没找到引用，不知道靠不靠谱
        @param words:
        @param timeout:
        @return:
        """
        logger.info(f"逐个输入: {words}")
        self.find(timeout=timeout).press_sequentially(words)
        logger.info("输入完成")

    def check(self, timeout=5):
        logger.info("复选框选中")
        self.find(timeout=timeout).check()
        logger.info("选中完成")

    def select_option(self, value: str, timeout=5):
        logger.info("下拉选择")
        self.find(timeout=timeout).select_option(value)
        logger.info("选择完成")

    def set_input_file(self, timeout=5, *args, **kwargs):
        """
        @param timeout:
        @param args:
        支持单个文件：'file.pdf'
        支持多个文件：['file1.txt', 'file2.txt']
        清空：[]
        @param kwargs: Upload buffer from memory
        files=[
            {"name": "test.txt", "mimeType": "text/plain", "buffer": b"this is a test"}
        ]
        @return:
        """
        logger.info("输入框型文件上传")
        self.find(timeout=timeout).set_input_files(*args, **kwargs)
        logger.info("上传完成")

    def set_files(self, file_path: str, timeout=5):
        logger.info("动态生成型文件上传")
        locator = self.find(timeout=timeout)
        with self._driver.page.expect_file_chooser() as fc_info:
            locator.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        logger.info("上传完成")

    def focus(self, timeout=5):
        logger.info("聚焦")
        self.find(timeout=timeout).focus()
        logger.info("聚焦完成")

    def drag_to(self, locator: Locator, timeout=5):
        logger.info("拖动到另外一个元素")
        self.find(timeout=timeout).drag_to(locator)
        logger.info("拖动完成")

    def drag_to_manually(self, locator: Locator, timeout=5):
        logger.info("手动模拟拖动")
        self.find(timeout=timeout).hover()
        self._driver.page.mouse.down()
        locator.hover()
        self._driver.page.mouse.up()
        logger.info("拖动完成")

    def scroll_into_view_if_needed(self, timeout=5):
        """
        正常做其他操作会自动滚动到可视区，自动不生效再用这个方法
        @param timeout:
        @return:
        """
        logger.info("元素滚动到可视区")
        self.find(timeout=timeout).scroll_into_view_if_needed()
        logger.info("滚动完成")

    def download(self, save_path: str, timeout=5):
        """
        下载
        @param save_path: 只要目录，文件名会自己生成
        @param timeout:
        @return:
        """
        logger.info("下载")
        with self._driver.page.expect_download() as download_info:
            self.find(timeout=timeout).click()
        download = download_info.value
        download.save_as(save_path + download.suggested_filename)
        logger.info("下载完成")

    def popup(self, timeout=5):
        """
        点击打开新页签，并返回新页签的page
        @param timeout:
        @return:
        """
        logger.info("打开新页签")
        with self._driver.page.expect_popup() as popup:
            self.find(timeout=timeout).click()
        new_page = popup.value
        return new_page

    # 断言
    def assert_checked(self, timeout=5):
        logger.info("断言：复选框是否选中")
        expect(self.find(timeout=timeout)).to_be_checked()
        logger.info("断言完成")

    def assert_visible(self, timeout=5):
        logger.info("断言：是否可见")
        expect(self.find(timeout=timeout)).to_be_visible()
        logger.info("断言完成")

    def assert_hidden(self, timeout=5):
        logger.info("断言：是否隐藏")
        expect(self.find(timeout=timeout)).to_be_hidden()
        logger.info("断言完成")

    def assert_text_ct(self, text: str, timeout=5):
        logger.info(f"断言：是否包含文本-{text}")
        expect(self.find(timeout=timeout)).to_contain_text(text)
        logger.info("断言完成")

    def assert_text_eq(self, text: str, timeout=5):
        logger.info(f"断言：是否等于文本-{text}")
        expect(self.find(timeout=timeout)).to_have_text(text)
        logger.info("断言完成")

    def assert_count_eq(self, count, timeout=5):
        logger.info(f"断言：locator定位到几个元素")
        expect(self.find(timeout=timeout)).to_have_count(count)
        logger.info("断言完成")

    def screenshot(self, file_path, timeout=5, full_screen=True):
        logger.info("截屏")
        if full_screen is True:
            self._driver.shot(file_path)
        else:
            self.find(timeout=timeout).screenshot(path=file_path)
        logger.info("截屏完成")


if __name__ == '__main__':
    pass
