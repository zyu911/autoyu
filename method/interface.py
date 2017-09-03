# -*- coding: utf-8 -*-


class MethodInterface(object):
    def latest(self):
        """
            获取最新的5分钟K线数据
        :return:
        """
        raise '你没有定义返回最新数据的方法!'