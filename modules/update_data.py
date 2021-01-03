# coding: utf-8

import datetime
import glob
import os
import shutil

import pandas as pd
from pandas import DataFrame, Series
from base_path import *


def _get_latest_fetch_date(fname):
    files = glob.glob(BASE_PATH + "/data/fetched/{}*.csv".format(fname))
    latest_fetch_date = datetime.datetime.strptime('20200101', '%Y%m%d')
    for file_name in files:
        date_str = file_name.split('/')[-1].replace(fname, '').replace('_', '').replace('.csv', '')
        fetch_date = datetime.datetime.strptime(date_str, '%Y%m%d')
        if latest_fetch_date < fetch_date:
            latest_fetch_date = fetch_date
    return latest_fetch_date.strftime('%Y%m%d')


def update_data():
    # ../data/fetched/fname_date.csv (最新日付) → ../data/latest/fname.date.csv

    # 対象のfnameリストを生成
    fname_list = []
    f = open(BASE_PATH + '/url_list.txt', 'r')
    for val in f.read().split('\n'):
        if 'output_name=' in val:
            fname_list.append(val.replace('output_name=', ''))

    # 各fnameについて、最新日付のcsvをlatestにコピー
    for fname in fname_list:
        latest_fetch_date = _get_latest_fetch_date(fname)
        shutil.copy(BASE_PATH + '/data/fetched/{}_{}.csv'.format(fname, latest_fetch_date), BASE_PATH + '/data/latest/{}.csv'.format(fname))


