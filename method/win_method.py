# -*- coding: utf-8 -*-
from method.interface import MethodInterface


class PicToData(MethodInterface):
    def __init__(self):
        pass

    def latest(self):
        print('获取最新K线数据!')