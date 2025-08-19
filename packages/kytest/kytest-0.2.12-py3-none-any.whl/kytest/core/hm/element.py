import time

from .driver import HmDriver

from kytest.utils.log import logger


class Elem(object):
    """
    鸿蒙元素定义
    https://github.com/codematrixer/hmdriver2
    """

    def __init__(self,
                 driver: HmDriver = None,
                 **kwargs):
        """
        @param driver: 安卓驱动
        @param watch: 需要处理的异常弹窗定位方式列表
        """
        self._driver = driver
        self._watch = kwargs.pop('watch', None)
        self._kwargs = kwargs

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # 公共方法
    def _match(self, text):
        """
        判断元素是否存在当前页面
        @return:
        """
        _element = self._driver.d(text=text)
        result = text if _element.exists(timeout=0.1) else None
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
        增加截图的方法
        @param timeout: 每次查找时间
        @param n：失败后重试的次数
        @return:
        """
        logger.info(f"查找控件: {self._kwargs}")
        _element = self._driver.d(**self._kwargs)

        if self._watch:
            self.pop_check()

        retry_count = n
        if _element.find_component(wait_time=timeout):
            logger.info(f"查找成功")
            return _element
        else:
            if retry_count > 0:
                for count in range(1, retry_count + 1):
                    logger.info(f"第{count}次重试...")
                    if self._watch:
                        self.pop_check()
                    if _element.find_component(wait_time=timeout):
                        logger.info(f"查找成功")
                        return _element

            logger.info("查找失败")
            if n > 0:
                self._driver.shot("查找失败")
            raise Exception(f"控件: {self._kwargs}, 查找失败")

    def exists(self, timeout=5):
        logger.info(f"判断控件{self._kwargs}是否存在")
        return self._driver.d(**self._kwargs).exists(wait_time=timeout, retries=0)

    def get_text(self, timeout=5):
        logger.info(f"获取控件{self._kwargs}的文本")
        return self.find(timeout=timeout).text

    def click_exists(self, timeout=5):
        logger.info(f"控件{self._kwargs}存在才点击")
        try:
            self.find(timeout=timeout, n=0).click()
            logger.info("点击完成")
        except:
            logger.info("不存在，不进行操作")

    def click(self, timeout=5):
        logger.info(f"控件{self._kwargs}点击")
        self.find(timeout=timeout).click()
        logger.info("点击完成")

    def input(self, text, timeout=5, clear=False):
        logger.info(f"控件{self._kwargs}输入文本: {text}")
        element = self.find(timeout=timeout)
        if clear is True:
            element.clear_text()
        element.input_text(text)
        logger.info("输入完成")









