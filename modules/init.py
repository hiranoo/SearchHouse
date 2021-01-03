# coding: utf-8

import os
from base_path import *

def init():
    new_path_list = ['/data', '/data/fetched', '/data/selected', '/data/latest', '/data/sending']

    for new_path in new_path_list:
        new_path = BASE_PATH + new_path
        if not os.path.exists(new_path):
            os.mkdir(new_path)
