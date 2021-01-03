# coding: utf-8

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import datetime
import time
import re
import sys, os
import glob
import shutil
from gmail_api_helpers import *
from process_data import *
from fetch_data import *
from update_data import *
from select_data import *
from send_data import *
from base_path import *
from init import *

"""
1. fetch data from suumo -- ./data/*_date.csv
2. update data to be latest -- ./latest/*.csv
3. select some data from latest data -- not csv, just a DataFrame
4. add data to the selected data, refering detail link -- DataFrame
5. select favorite data from 4's data -- ./favorite/*_date.csv
6. send favorite data (choose all or new)
"""

def get_fetch_needs():
    csvs = glob.glob(BASE_PATH + '/data/fetched/*.csv')
    today = datetime.datetime.now().strftime('%Y%m%d')
    needs = 1
    for csv in csvs:
        if today in csv:
            needs = 0
            break
    return needs


if __name__ == '__main__':
    columns = ['near1', 'walk1', 'commute', 'age', 'area', 'detail_room_plan', 'direction', 'available_date', 'monthly', 'link']
    
    # Create data directiories if unexist
    init()
   
    # suumo --> ./data/fetched
    do_fetch = get_fetch_needs()
    if do_fetch:
        fetch_basic_data()
    
    # ./data/fetched --> ./data/latest
    update_data()
    
    # ./data/latest --> ./data/selected
    select_and_save_data()
    
    # ./data/selected --> ./data/sending
    send_data('all', columns) # arg0: 'all' or 'new', arg1: columns to show
