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
from kytest.utils.config import kconfig

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
        host = kconfig['base_url']
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
        default_headers: dict = kconfig['headers']
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
    def assertStatus(status_code):
        """
        状态码
        """
        actual_code = ResponseResult.status_code
        logger.info(f"断言: {actual_code} 等于 {status_code}")
        assert (actual_code == status_code), f"状态码错误: {actual_code}"

    @staticmethod
    def assertSchema(schema, response=None) -> None:
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
    def assertEq(path: str, value):
        """
        等于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 等于 {value}")
                    assert _search_value == value, f'匹配到的第{i + 1}个结果: {_search_value} 不等于 {value}'
            else:
                logger.info(f"断言: {search_value} 等于 {value}")
                assert search_value == value, f"{search_value} 不等于 {value}"
        else:
            logger.info(f"断言: {search_value} 等于 {value}")
            assert search_value == value, f"{search_value} 不等于 {value}"

    @staticmethod
    def assertNotEq(path: str, value):
        """
        不等于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 不等于 {value}")
                    assert _search_value != value, f'匹配到的第{i + 1}个结果: {_search_value} 不应该等于 {value}'
            else:
                logger.info(f"断言: {search_value} 不等于 {value}")
                assert search_value != value, f'{search_value} 不应该等于 {value}'
        else:
            logger.info(f"断言: {search_value} 不等于 {value}")
            assert search_value != value, f'{search_value} 不应该等于 {value}'

    @staticmethod
    def assertLenEq(path: str, value):
        """
        长度等于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if search_value:
            for _search_value in search_value:
                if not isinstance(_search_value, list):
                    logger.info(f"断言: {len(search_value)} 等于 {value}")
                    assert len(search_value) == value, f'{len(search_value)} 不等于 {value}'
                    break
                else:
                    logger.info(f"断言: {len(_search_value)} 等于 {value}")
                    assert len(_search_value) == value, f'{len(_search_value)} 不等于 {value}'
        else:
            logger.info(f"断言: {len(search_value)} 等于 {value}")
            assert len(search_value) == value, f'{len(search_value)} 不等于 {value}'

    @staticmethod
    def assertLenGt(path: str, value):
        """
        长度大于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if search_value:
            for _search_value in search_value:
                if not isinstance(_search_value, list):
                    logger.info(f"断言: {len(search_value)} 大于 {value}")
                    assert len(search_value) > value, f'{len(search_value)} 应该大于 {value}'
                    break
                else:
                    logger.info(f"断言: {len(_search_value)} 大于 {value}")
                    assert len(_search_value) > value, f'{len(_search_value)} 应该大于 {value}'
        else:
            logger.info(f"断言: {len(search_value)} 大于 {value}")
            assert len(search_value) > value, f'{len(search_value)} 应该大于 {value}'

    @staticmethod
    def assertLenLt(path: str, value):
        """
        长度小于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if search_value:
            for _search_value in search_value:
                if not isinstance(_search_value, list):
                    logger.info(f"断言: {len(search_value)} 小于 {value}")
                    assert len(search_value) < value, f'{len(search_value)} 应该小于 {value}'
                    break
                else:
                    logger.info(f"断言: {len(_search_value)} 小于 {value}")
                    assert len(_search_value) < value, f'{len(_search_value)} 应该小于 {value}'
        else:
            logger.info(f"断言: {len(search_value)} 小于 {value}")
            assert len(search_value) < value, f'{len(search_value)} 应该小于 {value}'

    @staticmethod
    def assertGt(path: str, value):
        """
        大于
        """

        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 大于 {value}")
                    assert float(_search_value) > value, f'匹配到的第{i + 1}个结果: {_search_value} 应该大于 {value}'
            else:
                assert False, '匹配结果为空，断言失败'
        else:
            logger.info(f"断言: {search_value} 大于 {value}")
            assert float(search_value) > value, f"{search_value} 应该大于 {value}"

    @staticmethod
    def assertLt(path: str, value):
        """
        小于
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 小于 {value}")
                    assert float(_search_value) < value, f'匹配到的第{i + 1}个结果: {_search_value} 应该小于 {value}'
            else:
                assert False, '匹配结果为空，断言失败'
        else:
            logger.info(f"断言: {search_value} 小于 {value}")
            assert float(search_value) < value, f"{search_value} 应该小于 {value}"

    @staticmethod
    def assertRg(path: str, start, end):
        """
        范围
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 大于等于{start}，小于等于{end}")
                    assert (float(_search_value) >= start) and (float(_search_value) <= end), \
                        f'匹配到的第{i + 1}个结果: {_search_value} 不在[{start}, {end}]范围内'
            else:
                assert False, '匹配结果为空，断言失败'
        else:
            logger.info(f"断言: {search_value} 大于等于{start}，小于等于{end}")
            assert (float(search_value) >= start) and (float(search_value) <= end), \
                f'{search_value} 不在[{start}, {end}]范围内'

    @staticmethod
    def assertIn(path: str, value):
        """
        被包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 被 {value} 包含")
                    assert _search_value in value, f'匹配到的第{i + 1}个结果: {_search_value} 应该被 {value} 包含'
            else:
                logger.info(f"断言: {search_value} 被 {value} 包含")
                assert search_value in value, f"{search_value} 应该被 {value} 包含"
        else:
            logger.info(f"断言: {search_value} 被 {value} 包含")
            assert search_value in value, f"{search_value} 应该被 {value} 包含"

    @staticmethod
    def assertNotIn(path: str, value):
        """
        不被包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 不被 {value} 包含")
                    assert _search_value not in value, f'匹配到的第{i + 1}个结果: {_search_value} 应该不被 {value} 包含'
            else:
                logger.info(f"断言: {search_value} 不被 {value} 包含")
                assert search_value not in value, f"{search_value} 应该不被 {value} 包含"
        else:
            logger.info(f"断言: {search_value} 不被 {value} 包含")
            assert search_value not in value, f"{search_value} 应该不被 {value} 包含"

    @staticmethod
    def assertCt(path: str, value):
        """
        包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 包含 {value}")
                    assert value in _search_value, f'匹配到的第{i + 1}个结果: {_search_value} 应该包含 {value}'
            else:
                logger.info(f"断言: {search_value} 包含 {value} ")
                assert value in search_value, f"{search_value} 应该包含 {value}"
        else:
            logger.info(f"断言: {search_value} 包含 {value} ")
            assert value in search_value, f"{search_value} 应该包含 {value}"

    @staticmethod
    def assertNotCt(path: str, value):
        """
        包含
        """
        logger.info(f'查找"{path}"')
        search_value = jmespath.search(path, ResponseResult.response)
        if isinstance(search_value, list):
            if search_value:
                for i, _search_value in enumerate(search_value):
                    logger.info(f"断言: {_search_value} 不包含 {value}")
                    assert value not in _search_value, f'匹配到的第{i + 1}个结果: {_search_value} 不应该包含 {value}'
            else:
                logger.info(f"断言: {search_value} 不包含 {value} ")
                assert value not in search_value, f"{search_value} 不应该包含 {value}"
        else:
            logger.info(f"断言: {search_value} 不包含 {value} ")
            assert value not in search_value, f"{search_value} 不应该包含 {value}"

