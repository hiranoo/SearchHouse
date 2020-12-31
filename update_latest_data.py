# coding: utf-8

import datetime
import glob
import os
import re
import shutil
import smtplib
import sys
import time
import requests

import pandas as pd
from pandas import DataFrame, Series
from bs4 import BeautifulSoup

from gmail_api_helpers import *
from search_house_helpers import *


if __name__ == '__main__':
    # 更新されたデータの、検索条件名と更新日のリストを取得
    update_list = judge_update()
    new_df = pd.DataFrame()
    done_df = pd.DataFrame()
    for name, date in update_list.items():
        new, done = update(name, date)
        new_df.append(new) 
        done_df.append(done)

    # 希望条件の物件に絞り込む & メール送信
    mail_date = datetime.datetime.today().strftime('%Y%m%d')
    if len(new_df) > 0:
        #new_df = get_desired_rooms(new_df)
        contents = "test"
        send_email(new_df, "新着 {}件 @{}".format(len(new_df), mail_date), contents)
    if len(done_df) > 0:
        #done_df = get_desired_rooms(done_df)
        contents = "test"
        send_email(done_df, "掲載終了 {}件 @{}".format(len(done_df), mail_date), contents)
    
