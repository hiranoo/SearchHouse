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
import smtplib
from gmail_api_helpers import *

"""
最新物件ファイルを生成・更新する

1. update timestamp in another file
2. add new rooms
3. delete too old rooms that are no more posted.
"""

def get_latest_fetch_date(output_name):
    files = glob.glob("./data/{}*.csv".format(output_name))
    latest_fetch_date = datetime.datetime.strptime('20200101', '%Y%m%d')
    for file_name in files:
        date_str = file_name.split('/')[-1].replace(output_name, '').replace('_', '').replace('.csv', '')
        fetch_date = datetime.datetime.strptime(date_str, '%Y%m%d')
        if latest_fetch_date < fetch_date:
            latest_fetch_date = fetch_date
    return latest_fetch_date


def get_timestamp(output_name):
    res = ""
    try:
        with open('./timestamp/{}'.format(output_name), mode='r') as f:
            value = f.read().rstrip()
            # convert into datetime-object
            res = datetime.datetime.strptime(value, '%Y%m%d')
    except:
        res = datetime.datetime(2000, 1, 1)
    return res

def judge_update():
    update_list = {}

    # read room list files
    output_name_list = []
    f = open('url_list.txt', 'r')
    for val in f.read().split('\n'):
        if 'output_name=' in val:
            output_name_list.append(val.replace('output_name=', ''))

    # judge if you should update latest file or not, for each file
    for output_name in output_name_list:
        # get latest date of fetching suumo data
        latest_fetch_date = get_latest_fetch_date(output_name)
        # get timestamp of last update
        timestamp_date = get_timestamp(output_name)

        if latest_fetch_date > timestamp_date:
            # update timestamp file
            with open('./timestamp/{}'.format(output_name), mode='w') as f:
                f.write(latest_fetch_date.strftime('%Y%m%d'))
            
            # add to update_list
            update_list[output_name] = latest_fetch_date.strftime('%Y%m%d')

    return update_list

def update(name, date):
    older_file = "./latest/{}.csv".format(name)
    newer_file = "./data/{}_{}.csv".format(name, date)
    new_df = pd.DataFrame()
    done_df = pd.DataFrame()
    if os.path.exists(older_file):
        older_df = pd.read_csv(older_file)
        newer_df = pd.read_csv(newer_file)

        # 新着物件を抽出
        new_df = newer_df[-newer_df['link'].isin(older_df['link'])]

        # 掲載終了物件を抽出
        done_df = older_df[-older_df['link'].isin(newer_df['link'])]

    # update: cp newer_file to order_file
    shutil.copy(newer_file, older_file)

    return (new_df, done_df)


def get_desired_rooms(df):
    #,building_name,address,nearest1,walk,nearest2,walk2,nearest3,walk,age,height,office,commute,change,
    #floor,rent,admin,deposit,reward,room_plan,area,link

    d_age = df['age'] < 35
    d_floor = df['height'] > df['floor']
    d_money = (df['rent'] + df['admin']) <= 75000

    return df[d_age * d_floor * d_money]


def send_email(df, subject, message_text):
    # create a csv file of new rooms list
    df.to_csv('./tmp/rooms.csv', sep = ',',encoding='utf-8')

    # authorize gmail api
    service = authorize()
    
    # create message
    sender = "automf03@gmail.com"
    to = "trivalworks@gmail.com"
    filepath = "./tmp/rooms.csv"
    message = create_message_with_attachment(sender, to, subject, message_text, filepath)

    # send message
    send_message(service=service, user_id='me', message=message)

