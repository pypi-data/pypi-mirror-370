"""
@Author: kang.yang
@Date: 2025/4/14 15:22
pip install chardet==5.2.0
pip install baidu-aip==4.16.13
"""
import json
from aip import AipOcr
from kytest.utils.config import FileConfig


def get_position(source_img_path, keyword: str):
    """
    @Author: kang.yang
    @Date: 2025/4/14 14:50
    """

    # 初始化AipOcr
    APP_ID = FileConfig.get_ocr('app_id')
    API_KEY = FileConfig.get_ocr('api_key')
    SECRET_KEY = FileConfig.get_ocr('secret_key')
    if APP_ID and API_KEY and SECRET_KEY:
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    else:
        raise KeyError('OCR配置不能为空')

    # 读取图片
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = get_file_content(source_img_path)  # 替换为你的图片路径

    # 设置可选参数
    options = {
        "language_type": "CHN_ENG",  # 中英文混合
        "detect_direction": "true",  # 检测图像方向
        "detect_language": "true",  # 检测语言类型
        "probability": "true"  # 返回识别结果中每一行的置信度信息
    }

    # 调用OCR服务
    result = client.accurate(image, options)

    # 打印识别结果
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # 解析识别结果，获取文字及其坐标
    if 'words_result' in result:
        for word in result['words_result']:
            text = word['words']  # 文字内容
            location = word['location']  # 坐标信息
            print(f"Recognized Text: {text}")
            print(f"Location: {location}")
            if text == keyword:
                center_x = location['left'] + location['width'] // 2
                center_y = location['top'] + location['height'] // 2
                print(f'中心坐标: ({center_x}, {center_y})')
                return center_x, center_y
    else:
        print('识别失败')
        return None

