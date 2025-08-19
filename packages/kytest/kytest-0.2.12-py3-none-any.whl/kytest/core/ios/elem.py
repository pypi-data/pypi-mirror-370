import time
import threading

from kytest.utils.log import logger
from .local_driver import Driver


lock = threading.Lock()


# 链式调用临时存储定位方式
class ChildLocator:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.type = 'child'


class Elem(object):
    """
    IOS原生元素定义
    https://github.com/openatx/facebook-wda
    """

    def __init__(self, driver: Driver = None, watch: list = None, **kwargs):
        """
        @param driver: IOS驱动
        @param watch: 异常弹窗处理定位方式列表
        """
        self._kwargs = kwargs
        self._driver = driver
        self._xpath = kwargs.get('xpath', None)
        self._watch = watch
        self.locators = []

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # 链式调用方法
    def child(self, *args, **kwargs):
        self.locators.append(ChildLocator(*args, **kwargs))
        return self

    def _match(self, text):
        """
        判断元素是否存在当前页面
        @return:
        """
        _element = self._driver.d(text=text)
        result = text if _element.wait(timeout=0.1,
                                       raise_error=False) else None
        return result

    def pop_check(self, timeout=3):
        logger.info(f"开始弹窗检测: {self._watch}")
        # 多线程match，如果match到，获取第一个非None内容，进行点击
        # match完休息1s，如果休息3s也没有match到，就停止（定义一个flag，match到就清零）
        # 如果3s内仍然能match到就继续（如果flag大于3就停止）
        _build_info = ["允许", "使用App时允许", "始终允许", "同意"]
        if self._watch is True:
            loc_list = _build_info
        else:
            loc_list = list(set(_build_info + self._watch))
        flag = timeout
        while flag > 0:
            import concurrent.futures

            logger.info(f"匹配: {loc_list}")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self._match, loc_list)
                results = [item for item in results if item is not None]

            if results:
                logger.info(f"匹配到: {results}")
                self._driver.d(text=results[0]).click()
                logger.info("点击成功")
                flag = timeout
            else:
                logger.info("匹配失败")

            flag -= 1
            time.sleep(1)
        logger.info("结束检测")

    def find(self, timeout=5, n=3):
        """
        针对元素定位失败的情况，抛出KError异常
        @param timeout:
        @param n: 重试次数
        ["允许", "同意"]
        @return:
        """
        logger.info(f"查找控件: {self._kwargs}")
        # 元素定义
        _element = self._driver.d.xpath(self._xpath) if \
            self._xpath else self._driver.d(**self._kwargs)

        # 链式调用方法叠加
        if self.locators:
            logger.info(f"链式调用: {self.locators}")
            for loc_obj in self.locators:
                if loc_obj.type == "child":
                    _element = _element.child(*loc_obj.args, **loc_obj.kwargs)

        if self._watch:
            self.pop_check()

        # 定位过程
        retry_count = n
        if _element.wait(timeout=timeout):
            logger.info(f"查找成功")
            return _element
        else:
            for count in range(1, retry_count + 1):
                logger.info(f"定位失败第{count}次重试...")
                if self._watch:
                    self.pop_check()
                if _element.wait(timeout=timeout):
                    logger.info(f"查找成功")
                    return _element

            logger.info("查找失败")
            if n > 0:
                self._driver.shot("查找失败")
            raise Exception(f"控件: {self._kwargs}, 查找失败")
        # try:
        #     if _element.wait(timeout=timeout):
        #         logger.info(f"查找成功")
        #         return _element
        #     else:
        #         for count in range(1, retry_count + 1):
        #             logger.info(f"定位失败第{count}次重试...")
        #             if self._watch:
        #                 self.pop_check()
        #             if _element.wait(timeout=timeout):
        #                 logger.info(f"查找成功")
        #                 return _element
        #
        #         logger.info("查找失败")
        #         self._driver.shot("查找失败")
        #         raise Exception(f"控件: {self._kwargs}, 查找失败")
        # except ConnectionError:
        #     logger.info('wda连接失败, 进行重连!!!')
        #     self._driver.util.start_wda()
        #
        #     for count in range(1, retry_count + 1):
        #         logger.info(f"连接失败第{count}次重试...")
        #         if self._watch:
        #             self.pop_check()
        #         if _element.wait(timeout=timeout):
        #             logger.info(f"查找成功")
        #             return _element

    def get_text(self, timeout=5):
        logger.info(f"获取控件{self._kwargs}的文本")
        return self.find(timeout=timeout).text

    def exists(self, timeout=5):
        """
        判断元素是否存在当前页面
        @param timeout:
        @return:
        """
        logger.info(f"判断控件{self._kwargs}是否存在")
        result = False
        try:
            _element = self.find(timeout=timeout, n=0)
            result = True
        except:
            result = False
        finally:
            logger.info(result)
            return result

    def _adapt_center(self, timeout=5, retry=3):
        """
        修正控件中心坐标
        """
        bounds = self.find(timeout=timeout, n=retry).bounds
        left_top_x, left_top_y, width, height = \
            bounds.x, bounds.y, bounds.width, bounds.height
        center_x = int(left_top_x + width/2)
        center_y = int(left_top_y + height/2)
        logger.info(f'{center_x}, {center_y}')
        return center_x, center_y

    def click_exists(self, timeout=5):
        """
        存在才点击
        @param: retry，重试次数
        @param: timeout，每次重试超时时间
        """
        logger.info(f'控件{self._kwargs}存在才点击')
        try:
            x, y = self._adapt_center(timeout=timeout, retry=0)
            self._driver.d.appium_settings({"snapshotMaxDepth": 0})
            self._driver.click(x, y)
            self._driver.d.appium_settings({"snapshotMaxDepth": 50})
            logger.info("点击完成")
        except:
            logger.info("不存在，不进行操作")

    def click(self, timeout=5):
        """
        单击
        @param: retry，重试次数
        @param: timeout，每次重试超时时间
        """
        logger.info(f'控件{self._kwargs}点击')
        x, y = self._adapt_center(timeout=timeout)
        self._driver.d.appium_settings({"snapshotMaxDepth": 0})
        self._driver.click(x, y)
        self._driver.d.appium_settings({"snapshotMaxDepth": 50})
        logger.info("点击完成")

    def input(self, text, timeout=5, clear=False):
        """输入内容"""
        logger.info(f"控件{self._kwargs}输入: {text}")
        element = self.find(timeout=timeout)
        if clear is True:
            element.clear_text()
        element.set_text(text)
        logger.info("输入完成")



















