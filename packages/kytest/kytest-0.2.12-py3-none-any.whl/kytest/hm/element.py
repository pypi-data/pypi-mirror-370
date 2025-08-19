import time

from kytest.hm.driver import HmDriver

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
        logger.info(f"查找: {self._kwargs}")
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
            self._driver.shot("查找失败")
            raise Exception(f"控件: {self._kwargs}, 查找失败")

    def exists(self, timeout=5):
        logger.info("是否存在")
        return self._driver.d(**self._kwargs).exists(wait_time=timeout, retries=0)

    def info(self):
        logger.info("获取控件信息")
        return self.find().info

    def count(self):
        logger.info("获取控件数量")
        return self.find().count

    def get_text(self, timeout=5):
        logger.info("获取文本")
        return self.find(timeout=timeout).text

    def click(self, timeout=5):
        logger.info("点击")
        self.find(timeout=timeout).click()
        logger.info("点击完成")

    def double_click(self, timeout=5):
        logger.info("双击")
        self.find(timeout=timeout).double_click()
        logger.info("双击完成")

    def long_click(self, timeout=5):
        logger.info("长按")
        self.find(timeout=timeout).long_click()
        logger.info("长按完成")

    def drag_to(self, timeout=5, *args, **kwargs):
        logger.info("拖动")
        self.find(timeout=timeout).drag_to(*args, **kwargs)
        logger.info("拖动完成")

    def pinch_in(self, timeout=5, *args, **kwargs):
        logger.info("缩小")
        self.find(timeout=timeout).pinch_in(*args, **kwargs)
        logger.info("缩小完成")

    def pinch_out(self, timeout=5, *args, **kwargs):
        logger.info("放大")
        self.find(timeout=timeout).pinch_out(*args, **kwargs)
        logger.info("放大完成")

    def input(self, text, timeout=5):
        logger.info(f"输入: {text}")
        self.find(timeout=timeout).input_text(text)
        logger.info("输入完成")

    def clear(self, timeout=5, *args, **kwargs):
        logger.info("清空")
        self.find(timeout=timeout).clear_text(*args, **kwargs)
        logger.info("清空完成")

    def assert_exists(self, timeout=5):
        logger.info("断言控件存在")
        assert self.exists(timeout=timeout)
        logger.info("断言完成")

    def assert_text_eq(self, text, timeout=5):
        logger.info(f"断言控件文本等于: {text}")
        assert text == self.get_text(timeout=timeout)
        logger.info("断言完成")

    def assert_text_ct(self, text, timeout=5):
        logger.info(f"断言控件文本包括: {text}")
        assert text in self.get_text(timeout=timeout)
        logger.info("断言完成")

    def screenshot(self, file_path, timeout=5):
        logger.info("截屏")
        try:
            self.find(timeout=timeout)
        except Exception as e:
            raise e
        else:
            self._driver.shot(file_path)
        finally:
            logger.info("截屏完成")


if __name__ == '__main__':
    pass







