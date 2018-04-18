# -*- coding: utf-8 -*-
import logging


class MethodInterface(object):
    def __init__(self):
        logging.basicConfig(filename='\\\\Mac\\Home\\Desktop\\run_log.log',
                    format='%(asctime)s - %(message)s - %(name)s - %(levelname)s - %(module)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=10)

    def latest(self):
        """
            获取最新的5分钟K线数据
        :return:
        """
        raise '你没有定义返回最新数据的方法!'