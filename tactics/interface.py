# -*- coding: utf-8 -*-


class BaseTacticsInterface(object):

    def get_data(self):
        raise u'你没有定义获取数据的方法!'

    def ret_tactics(self):
        raise u'你没有定义返回策略的方法!'