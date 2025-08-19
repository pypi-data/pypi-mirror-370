# @Time    : 2022/2/22 9:35
# @Author  : kang.yang@qizhidao.com
# @File    : request.py
import json as json_util
import logging
import requests
import jmespath
import time

from functools import wraps
from requests.packages import urllib3
from urllib import parse
from jsonschema import validate, ValidationError
from kytest.utils.log import logger
from kytest.utils.config import FileConfig

# 去掉requests本身的日志
urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.CRITICAL)

# 去掉不设置证书的报警
urllib3.disable_warnings()


def formatting(msg):
    """formatted message"""
    if isinstance(msg, dict):
        return json_util.dumps(msg, indent=2, ensure_ascii=False)
    return msg


def request(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("-------------- Request -----------------[🚀]")
        # 给接口带上默认域名
        # 从配置文件中读取域名
        host = FileConfig.get_api('base_url')
        # 如果接口路径不以http开头，把域名写到key为url的位置参数中或者第一个参数中
        if "url" in kwargs:
            path: str = kwargs.get("url", "")
            if not path.startswith('http'):
                url = parse.urljoin(host, path)
                kwargs["url"] = url
            else:
                url = path
        else:
            path = list(args)[1]
            if not path.startswith('http'):
                url = parse.urljoin(host, path)
                args_list = list(args)
                args_list[1] = url
                args = tuple(args_list)
            else:
                url = path

        # 请求头处理，写入登录态
        default_headers: dict = FileConfig.get_api('headers')
        user_set_headers = kwargs.pop("headers", {})
        _final_headers = {}
        if default_headers:
            _final_headers.update(default_headers)
        if user_set_headers:
            _final_headers.update(user_set_headers)
        if _final_headers:
            kwargs["headers"] = _final_headers

        # 更新超时时间
        timeout_user_set = kwargs.pop("timeout", None)  # 用例脚本中设置的超时时间
        kwargs["timeout"] = timeout_user_set if timeout_user_set else 10

        # 发送请求
        start_time = time.time()
        r = func(*args, **kwargs)
        end_time = time.time()
        takes = end_time - start_time

        # 输出请求参数日志
        logger.debug("[method]: {m} [url]: {u} [cost]: {c}s".format(m=func.__name__.upper(), u=url, c=round(takes, 3)))
        auth = kwargs.get("auth", "")
        if auth:
            logger.debug(f"[auth]:\n {formatting(auth)}")
        logger.debug(f"[headers]:\n {formatting(dict(r.request.headers))}")
        cookies = kwargs.get("cookies", "")
        if cookies:
            logger.debug(f"[cookies]:\n {formatting(cookies)}")
        params = kwargs.get("params", "")
        if params:
            logger.debug(f"[params]:\n {formatting(params)}")
        data = kwargs.get("static", "")
        if data:
            logger.debug(f"[static]:\n {formatting(data)}")
        json = kwargs.get("json", "")
        if json:
            logger.debug(f"[json]:\n {formatting(json)}")

        # 保存响应结果并输出日志
        status_code = r.status_code
        headers = r.headers
        content_type = headers.get("Content-Type")
        ResponseResult.status_code = status_code
        logger.info("-------------- Response ----------------")
        logger.debug(f"[status]: {status_code}")
        logger.debug(f"[headers]: {formatting(headers)}")
        try:
            resp = r.json()
            logger.debug(f"[type]: json")
            logger.debug(f"[response]:\n {formatting(resp)}")
            ResponseResult.response = resp
        except Exception:
            # 非json响应数据，根据响应内容类型进行判断
            logger.info("response is not json type static.")
            if content_type is not None:
                if "text" not in content_type:
                    logger.debug(f"[type]: {content_type}")
                    logger.debug(f"[response]:\n {r.content}")
                    ResponseResult.response = r.content
                else:
                    logger.debug(f"[type]: {content_type}")
                    logger.debug(f"[response]:\n {r.text}")
                    ResponseResult.response = r.text
            else:
                logger.debug('ContentType为空，响应异常！！！')
                ResponseResult.response = r.text

        return r

    return wrapper


class ResponseResult:
    # 并发执行不会串数据，是因为我用的是多进程而不是多线程吧???
    status_code = 200
    response = None


class HttpReq(object):
    @request
    def get(self, url, params=None, verify=False, **kwargs):
        return requests.get(url, params=params, verify=verify, **kwargs)

    @request
    def post(self, url, data=None, json=None, verify=False, **kwargs):
        return requests.post(url, data=data, json=json, verify=verify, **kwargs)

    @request
    def put(self, url, data=None, json=None, verify=False, **kwargs):
        if json is not None:
            data = json_util.dumps(json)
        return requests.put(url, data=data, verify=verify, **kwargs)

    @request
    def delete(self, url, verify=False, **kwargs):
        return requests.delete(url, verify=verify, **kwargs)

    @property
    def response(self):
        """
        Returns the result of the response
        :return: response
        """
        return ResponseResult.response

    # 断言
    @staticmethod
    def assertStatusCode(status_code):
        """
        断言状态码
        """
        actual_code = ResponseResult.status_code
        logger.info(f"断言: {actual_code} 等于 {status_code}")
        assert (actual_code == status_code), f"状态码错误: {actual_code}"

    @staticmethod
    def assertJsonSchema(schema, response=None) -> None:
        """
        Assert JSON Schema
        doc: https://json-schema.org/
        """
        logger.info(f"assertSchema -> {formatting(schema)}.")

        if response is None:
            response = ResponseResult.response

        try:
            validate(instance=response, schema=schema)
        except ValidationError as msg:
            assert "Response static" == "Schema static", msg

    @staticmethod
    def assertEqual(path: str, value):
        """
        断言根据jmespath查到的值等于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 等于 {value}")
        assert search_value == value, f"{search_value} 不等于 {value}"

    @staticmethod
    def assertNotEqual(path: str, value):
        """
        断言根据jmespath查到的值不等于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 不等于 {value}")
        assert search_value != value, f'{search_value} 不应该等于 {value}'

    @staticmethod
    def assertGreaterThen(path: str, value):
        """
        断言根据jmespath查到的值大于value
        """

        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 大于 {value}")
        assert float(search_value) > value, f"{search_value} 应该大于 {value}"

    @staticmethod
    def assertLessThen(path: str, value):
        """
        断言根据jmespath查到的值小于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 小于 {value}")
        assert float(search_value) < value, f"{search_value} 应该小于 {value}"

    @staticmethod
    def assertLenEqual(path: str, value):
        """
        断言根据jmespath查到的值长度等于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {len(search_value)} 等于 {value}")
        assert len(search_value) == value, f'{len(search_value)} 不等于 {value}'

    @staticmethod
    def assertLenGreaterThen(path: str, value):
        """
        断言根据jmespath查到的值长度大于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {len(search_value)} 大于 {value}")
        assert len(search_value) > value, f'{len(search_value)} 应该大于 {value}'

    @staticmethod
    def assertLenLessThen(path: str, value):
        """
        断言根据jmespath查到的值长度小于value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {len(search_value)} 小于 {value}")
        assert len(search_value) < value, f'{len(search_value)} 应该小于 {value}'

    @staticmethod
    def assertIn(path: str, value):
        """
        断言根据jmespath查到的值被value包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 被 {value} 包含")
        assert search_value in value, f"{search_value} 应该被 {value} 包含"

    @staticmethod
    def assertNotIn(path: str, value):
        """
        断言根据jmespath查到的值不被value包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 不被 {value} 包含")
        assert search_value not in value, f"{search_value} 应该不被 {value} 包含"

    @staticmethod
    def assertContain(path: str, value):
        """
        断言根据jmespath查到的值包含value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 包含 {value} ")
        assert value in search_value, f"{search_value} 应该包含 {value}"

    @staticmethod
    def assertNotContain(path: str, value):
        """
        断言根据jmespath查到的值不包含value
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        logger.info(f"断言: {search_value} 不包含 {value} ")
        assert value not in search_value, f"{search_value} 不应该包含 {value}"


