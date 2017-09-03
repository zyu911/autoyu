# coding=UTF-8
import sys
import os
from mapper.util import Mapper
from controls import win_control
# import manual
# sys.path.append(os.path.dirname(__file__))
# print(os.path.dirname(__file__))
from conf import settings


def mapper_hook():
    Mapper.relation(settings.mapper)


if __name__ == "__main__":
    mapper_hook()
    control = win_control.WinControl()
    control.start()
    # worker = manual.Manual(None)
    # worker.get_time_price()
