# 依赖通过easyocr起一个识别服务
import requests

from kytest.utils.config import kconfig
from kytest.utils.log import logger


def ocr_discern(image_path, keyword):
    """ocr能力通过api提供"""
    # 定义请求的 URL 和参数
    url = kconfig['ocr_service']
    # url = 'http://127.0.0.1:5000/ocr'
    if not url:
        raise Exception('请传入ocr服务url')

    # 构建请求的数据
    data = {
        "keyword": keyword,
    }

    # 构建文件上传的数据
    files = {
        "image": open(image_path, "rb"),
    }

    # 发送 POST 请求
    response = requests.post(url, params=data, files=files)
    logger.debug(response.text)

    try:
        res = response.json().get("data")
        return res
    except:
        return False


if __name__ == '__main__':
    ocr_discern('test1.png', '查企业')


