"""
ClickMouse库
---
该库提供了鼠标点击操作的函数。

使用方法：
import clickmouse

# 点击鼠标左键
clickmouse.click_mouse(clickmouse.LEFT, 100, 100, 10) # 鼠标左键点击10次，延迟为100毫秒，按下时间为100毫秒
clickmouse.click_mouse(clickmouse.RIGHT, 100, 100, 10) # 鼠标右键点击10次，延迟为100毫秒，按下时间为100毫秒
"""

# 需要的库
import pyautogui
from typing import Literal
from time import sleep

# 内置变量
__version__ = '0.1.0'
__author__ = 'xystudio'

# 常量
INFINITE = -1
LEFT = pyautogui.LEFT
RIGHT = pyautogui.RIGHT

def click_mouse(button: Literal['left', 'right'], delay: int, press_time: int, time: int=1) -> None:
    '''
    按下鼠标处理函数
    :param button: 鼠标按键，可以是'left'或'right'
    :param delay: 延迟时间，单位为毫秒
    :param press_time: 按键时间，单位为毫秒
    :param time: 按键次数，-1表示无限循环
    '''
    pass