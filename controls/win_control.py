# -*- coding: utf-8 -*-
from tactics.interface import BaseTacticsInterface
from mapper.util import MyType


class WinControl(BaseTacticsInterface):
    __metaclass__ = MyType

    def __init__(self, method):
        self.method = method

    def start(self):
        self.method.latest()