# -*- coding: utf-8 -*-
from tactics.interface import BaseTacticsInterface


class WinControl(BaseTacticsInterface):

    def __init__(self, method):
        self.method = method

    def start(self):
        print(self.method.lasest())