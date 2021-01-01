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

from gmail_api_helpers import *
from search_house_helpers import *


def get_favorite_rooms(df):
    #,building_name,address,nearest1,walk,nearest2,walk2,nearest3,walk,age,height,office,commute,change,
    #floor,rent,admin,deposit,reward,room_plan,area,link
    # 
    d_age_t = df['age'] <= 20
    d_age_b = df['age'] > 0
    d_walk1 = df['walk1'] <= 12
    d_floor = df['height'] > df['floor']
    d_money = (df['rent'] + df['admin']) <= 70000
    d_change = df['change'] <= 3
    d_area = df['area'] >= 23
    d_nearest1 = '舎人ライナー' in df['nearest1'] 
    d_direction_negative = df['direction'].str.contains('-|北|西')
    d_available = df['available_date'].str.contains('即|1月|2月')

    return df[d_age_t*d_age_b*d_walk1*d_floor*d_money*d_change*d_area*d_nearest1*d_direction_negative*d_available]

def get_latest_dfs(filepath):
    files = glob.glob("./latest/*.csv")
    favorite_df = pd.DataFrame()
    count = 0
    for fil in files:
        df = pd.read_csv(fil)
        df = get_favorite_rooms(df)
        if count == 0:
            favorite_df = df
        else:
            favorite_df = pd.concat([favorite_df, df])
        count += 1
    return favorite_df
    

if __name__ == '__main__':
    file_path = './latest_favorite_rooms.csv'
    df = get_latest_dfs(file_path)

    subject = "最新物件リスト"
    message_text = ""
    send_email(df, file_path, subject, message_text)
    
