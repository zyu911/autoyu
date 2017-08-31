# coding=UTF-8
import logging
import win32gui

import pytesseract
import win32con
from PIL import ImageGrab


class Manual(object):
    def __init__(self, mental):
        logging.basicConfig(filename='\\\\Mac\\Home\\Desktop\\run_log.log',
                            format='%(asctime)s - %(message)s - %(name)s - %(levelname)s - %(module)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=10)
        self.mental = mental
        self.win = "Afx:00400000:b:00010003:00000006:0002035D"
        self.hwnd = None
        while not self.hwnd:
            self.hwnd = win32gui.FindWindow(self.win, None)
            if not self.hwnd:
                self.win = input('打开Spy++选择窗口交复制窗口类名:')

    def show(self):
        # windows handlers
        # hwnd = self.window.handle
        hwnd = win32gui.FindWindow(self.win, None)
        win32gui.ShowWindow(hwnd, 1)
        win32gui.SetForegroundWindow(hwnd)

    def get_time_price(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)  # 强行显示界面后才好截图
        win32gui.SetForegroundWindow(self.hwnd)  # 将窗口提到最前
        pic = win32gui.GetWindowRect(self.hwnd)

        hour_image = ImageGrab.grab((pic[2]-368, pic[1]+490, pic[2]-133, pic[1]+520))
        str_time = pytesseract.image_to_string(hour_image)  # 当前单时间交易
        hour_image.show()
        with open('\\\\Mac\\Home\\Desktop\\tmp.bmp', 'w') as F:
            hour_image.save(F)

