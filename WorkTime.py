# encoding=UTF-8
import datetime
import json
import logging
import sys
import time
import win32api
import win32gui

import pytesseract
import util
import win32con
from PIL import ImageGrab

from tactics import Astrowings

data = []
td = []


class WorkTime(object):

    def __init__(self):
        logging.basicConfig(filename='\\\\Mac\\Home\\Desktop\\run_log.log',
                    format='%(asctime)s - %(message)s - %(name)s - %(levelname)s - %(module)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=10)
        self.data = []  # 存储5分钟交易数据 [[22秒, 98交易量],...]
        self.time_now = None
        self.time_end = None  # 交易软件5分钟结束时间
        self.open = 0
        self.high = 0
        self.low = 0
        self.price = 0  # 当前最新成交价格
        self.win = "Afx:00400000:b:00010003:00000006:0002035D"
        self.hwnd = None
        self.exclude_t = ['09:05:00', '09:10:00', '09:15:00', '14:45:00' '14:50:00',
                          '14:55:00', '22:45:00', '22:50:00', '22:55:00']
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

    def exclude_time(self, t):
        t = t.split(' ')[1].split('.')[0]
        if not t.endswith(':00'):
            t += ':00'
        if t in self.exclude_t:
            return True
        return False

    @property
    def volume(self):   # 5分钟买卖次数
        return len(self.data)

    @property
    def turnover(self):  # 当前总成交量
        return 0

    def set_time_now_or_end(self, time):
        hour, minute, second = time.split(':')
        try:
            hour = int(hour)
            minute = int(minute)
            second = int(second)
        except Exception as E:
            print(time)
            return False

        t = datetime.datetime.now()
        tmp_min = minute - minute % 5
        end_h, end_m = util.time_diff(hour, tmp_min)
        self.time_now = datetime.datetime(t.year, t.month, t.day, hour, minute, second, 0)
        if not self.time_end:
            self.time_end = datetime.datetime(t.year, t.month, t.day, end_h, end_m, 0, 0)

        return True

    def set_price(self, price):
        self.price = price
        if self.open == 0: self.open = price
        self.high = price if self.high == 0 or self.high < price else self.high
        self.low = price if self.low == 0 or self.low > price else self.low
        return True

    def set_volume(self, time, present):
        second = time.split(':')[-1]
        if not self.data or (self.data[-1][0] != second and self.data[-1][1] == present):
            self.data.append([second, present])

    def clear(self):
        self.data = []  # 存储5分钟交易数据 [[22秒, 98交易量],...]
        self.time_end = None  # 交易软件5分钟结束时间
        self.open = 0
        self.high = 0
        self.low = 0
        self.price = 0  # 当前最新成交价格

    def get_data(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)  # 强行显示界面后才好截图
        # win32gui.SetForegroundWindow(self.hwnd)  # 将窗口提到最前
        pic = win32gui.GetWindowRect(self.hwnd)

        price_image = ImageGrab.grab((pic[2]-280, pic[1]+280, pic[2]-215, pic[1]+305))
        price = pytesseract.image_to_string(price_image, config="-psm 8 -c tessedit_char_whitelist=1234567890")

        hour_image = ImageGrab.grab((pic[2]-368, pic[1]+490, pic[2]-260, pic[1]+520))
        str_time = pytesseract.image_to_string(hour_image)  # 当前单时间交易

        try:
            price = float(price)
        except Exception:
            return False

        self.set_time_now_or_end(str_time)
        self.set_price(price)

        return True

    def push(self):
        # 发送数据
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)  # 强行显示界面后才好截图
        # win32gui.SetForegroundWindow(self.hwnd)  # 将窗口提到最前
        pic = win32gui.GetWindowRect(self.hwnd)
        # open
        open = ImageGrab.grab((pic[0]+59, pic[1]+168+48, pic[0]+120, pic[1]+193+48))

        # high
        high = ImageGrab.grab((pic[0]+59, pic[1]+213+48, pic[0]+120, pic[1]+240+48))
        # low
        low = ImageGrab.grab((pic[0]+59, pic[1]+258+48, pic[0]+120, pic[1]+285+48))
        # close
        close = ImageGrab.grab((pic[0]+59, pic[1]+306+48, pic[0]+120, pic[1]+330+48))
        try:
            ope = float(pytesseract.image_to_string(open, config="-psm 8 -c tessedit_char_whitelist=1234567890"))
            high = float(pytesseract.image_to_string(high, config="-psm 8 -c tessedit_char_whitelist=1234567890"))
            low = float(pytesseract.image_to_string(low, config="-psm 8 -c tessedit_char_whitelist=1234567890"))
            close = float(pytesseract.image_to_string(close, config="-psm 8 -c tessedit_char_whitelist=1234567890"))
        except Exception as E:
            return False
        return [self.str_time, ope, high, low, close, 10000, 0]
        # da = [self.str_time(), self.open, self.high, self.low, self.price, self.turnover, 0]
        # return da

    @property
    def str_time(self):
        return datetime.datetime.strftime(self.time_end, '%Y-%m-%d %H:%M:%S.000000')

    def sss(self):
        # [6,  3000.0, 3000-6, 3000+15, 'F', 'BAD', '2017-8-7 09:05:00']
        # [-6, 3000.0, 3000+6, 3000-15, 'F', 'OK', '2017-8-7 09:05:00']
        global td
        if not td:
            return False
        if td[-1][4] == 'T' and td[-1][0] > 0:
            if self.price <= td[-1][2]:
                td[-1][4] = 'F'
                td[-1][5] = 'BAD'
                print('Order BAD')
            if self.price >= td[-1][3]:
                td[-1][4] = 'F'
                td[-1][5] = 'OK'
                print('Order OK')
        elif td[-1][4] == 'T' and td[-1][0] < 0:
            if self.price >= td[-1][2]:
                td[-1][4] = 'F'
                td[-1][5] = 'BAD'
                print('Order BAD')
            if self.price <= td[-1][3]:
                td[-1][4] = 'F'
                td[-1][5] = 'OK'
                print('Order OK')

    def status_td(self):
        global td
        return True if td and td[-1][4] == 'F' else False

    def start(self):
        t = datetime.datetime.now()
        st0 = datetime.datetime(t.year, t.month, t.day, 0, 46)
        et0 = datetime.datetime(t.year, t.month, t.day, 10, 19)
        st1 = datetime.datetime(t.year, t.month, t.day, 10, 11)
        et1 = datetime.datetime(t.year, t.month, t.day, 11, 34)
        st2 = datetime.datetime(t.year, t.month, t.day, 13, 26)
        et2 = datetime.datetime(t.year, t.month, t.day, 19, 04)
        st3 = datetime.datetime(t.year, t.month, t.day, 20, 56)
        et3 = datetime.datetime(t.year, t.month, t.day, 23, 04)
        obj = Astrowings.AstroWings()
        win32gui.SetForegroundWindow(self.hwnd)  # 将窗口提到最前
        while 1:
            if not self.get_data():
                continue
            while st0 < self.time_now < et0 or st1 < self.time_now < et1 or \
                                    st2 < self.time_now < et2 or st3 < self.time_now < et3:

                if self.time_now < self.time_end:
                    sys.stdout.write('\r\033[1;31m%s\t\t%s\033[0m' % (self.time_now, self.price))
                    sys.stdout.flush()
                    self.sss()
                else:
                    global data
                    line = self.push()
                    while not line:
                        line = self.push()
                        print('5 min k line')
                        time.sleep(0.1)

                    if data:
                        line[6] = line[4] - data[-1][4]  # diff
                    data.append(line)
                    logging.log(logging.INFO, (u'>> %s 开%s, 高%s, 低%s, 收%s, 量%s, 涨跌%s <<' % (
                            line[0], line[1], line[2], line[3], line[4], line[5], line[6])))
                    if not self.exclude_time(self.str_time):
                        obj.data = data
                        li = obj.dict_test()
                        if td: print(td[-1])
                        for xx in li:
                            if data[-1][-1] == xx[0] and self.status_td():
                                if line[6] > 0:
                                    self.show()
                                    win32api.keybd_event(65, 0, 0, 0)  # push a
                                    win32api.keybd_event(65, 0, win32con.KEYEVENTF_KEYUP, 0)
                                    td.append([line[6],  line[4], line[4]-8, line[4]+15, 'T', '', self.str_time])
                                else:
                                    self.show()
                                    win32api.keybd_event(68, 0, 0, 0)  # push d
                                    win32api.keybd_event(68, 0, win32con.KEYEVENTF_KEYUP, 0)
                                    td.append([line[6], line[4], line[4]+8, line[4]-15, 'T', '', self.str_time])
                                logging.info(u'阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s] ===========>%s-->%s' %
                                             (xx[0], xx[1], xx[2], xx[3], xx[4], data[-1][0], data[-1][-1]))
                                print(u'====阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s]====' % (xx[0], xx[1], xx[2], xx[3], xx[4]))

                                break

                    with open('data.txt', 'w') as F:
                        F.write(json.dumps(data))
                    with open('data_td.txt', 'w') as F:
                        F.write(json.dumps(td))
                    self.clear()

                # t0 = time.time()
                self.get_data()
                # t1 = time.time()
                # print(t1-t0)
            else:
                print('非工作时间!')


def test():
    ex_t = ['09:05:00', '09:10:00', '09:15:00', '14:45:00' '14:50:00',
                          '14:55:00', '22:45:00', '22:50:00', '22:55:00']
    obj = Astrowings.AstroWings()
    obj.data = data[:-112]
    for line in data[-112:]:
        print(u'\n\033[1;33m%s >> 开%s, 高%s, 低%s, 收%s, 量%s, 涨跌%s <<\033[0m' % (
            line[0], line[1], line[2], line[3], line[4], line[5], line[6]))
        obj.data.append(line)
        li = obj.dict_test()
        if td: print(td[-1])
        # [6,  3000.0, 3000-6, 3000+15, 'F', 'BAD']
        # [-6, 3000.0, 3000+6, 3000-15, 'F', 'OK']
        if td and td[-1][4] == 'T' and td[-1][0] > 0:
            if line[3] <= td[-1][2]:
                td[-1][4] = 'F'
                td[-1][5] = 'BAD'
                print('Order BAD')
            if line[2] >= td[-1][3]:
                td[-1][4] = 'F'
                td[-1][5] = 'OK'
                print('Order OK')
        elif td and td[-1][4] == 'T' and td[-1][0] < 0:
            if line[2] >= td[-1][2]:
                td[-1][4] = 'F'
                td[-1][5] = 'BAD'
                print('Order BAD')
            if line[3] <= td[-1][3]:
                td[-1][4] = 'F'
                td[-1][5] = 'OK'
                print('Order OK')
        t = line[0].split(' ')[1].split('.')[0]
        if t not in ex_t:
            for xx in li:
                if line[-1] == xx[0] and True if not td or td[-1][4] == 'F' else False:
                    logging.info(u'阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s] ===========>%s-->%s' %
                                 (xx[0], xx[1], xx[2], xx[3], xx[4], data[-1][0], data[-1][-1]))
                    print(u'==============BUY=========>>>>>>>>%s' % line[-1])
                    print(u'====阀值:%s 策略:%s 概率:%.2f%% 赢利:%s 日志:[%s]====' % (xx[0], xx[1], xx[2], xx[3], xx[4]))
                    if line[-1] > 0:
                        print('push a(buy)')
                        td.append([line[6],  line[4], line[4]-8, line[4]+15, 'T', '', line[0]])
                    else:
                        print('push d(seed)')
                        td.append([line[6], line[4], line[4]+8, line[4]-15, 'T', '', line[0]])
                    break

        with open('test_data_td.txt', 'w') as F:
            F.write(json.dumps(td))

if __name__ == '__main__':

    if 1:
        try:
            with open('data.txt', 'r') as F:
                data = json.loads(F.read())
        except Exception as E:
            data = []
        try:
            with open('data_td.txt', 'r') as F:
                td = json.loads(F.read())
        except Exception as E:
            td = []
        if td: print(td[-1])
        # [6,  3000.0, 3000-6, 3000+15, 'F', 'BAD', "time"]
        # [-6, 3000.0, 3000+6, 3000-15, 'F', 'OK', "time"]

        obj = WorkTime()
        while 1:
            try:
                obj.start()
            except Exception as E:
                sys.stdout.write('\r\033[1;31m Main Error %s\033[0m' % E)
                sys.stdout.flush()
                time.sleep(0.2)
    else:
        try:
            with open('data.txt', 'r') as F:
                data = json.loads(F.read())
        except Exception as E:
            data = []

        try:
            with open('test_data_td.txt', 'r') as F:
                td = json.loads(F.read())
        except Exception as E:
            td = []

        test()

        print('==================>')
        x = 0.0
        y = 0.0
        z = 0
        for i in td:
            if i[5] == 'OK':
                x += 1
                z += 15
            if i[4] == 'F':
                y += 1
            print(i)
        print(x, y, z)
        print(u"======>%s ==>%s" % ((x/y*100), z-(y-x)*8-y*1.5))