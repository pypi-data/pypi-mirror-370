"""
@Author: kang.yang
@Date: 2025/2/12 14:16
"""
import time
import pyautogui
from kytest.utils.excel_util import Excel
from kytest.web.driver import Driver


print('从excel读取url列表')
excel = Excel('source_data.xlsx')
url_list = excel.read()
print('excel读取完毕')
print('开始爬取页面内容')
driver = Driver(browserName='firefox')
for i, url in enumerate(url_list):
    page_url = url[0]
    print(f"请求第{i+1}个页面: {page_url}")
    driver.goto(page_url)
    time.sleep(3)
    pyautogui.keyDown('command')
    pyautogui.press('s')
    pyautogui.keyUp('command')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    break
print('爬取页面内容完毕')
driver.close()









