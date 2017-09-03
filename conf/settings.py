# -*- coding: utf-8 -*-
from decouple import config
import os
from method import win_method
from controls import win_control

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

redis_host = config('REDIS_HOST')
redis_port = config('REDIS_PORT')

mapper = {
    win_control: win_method,
}