# coding: utf-8

import requests
import pandas as pd
from pandas import Series, DataFrame
import glob
from gmail_api_helpers import *
from process_data import *
from base_path import *


def _send_csv(subject, message_text, csv):
    # authorize gmail api
    service = authorize()
    
    # create message
    sender = "automf03@gmail.com"
    to = "trivalworks@gmail.com"
    message = create_message_with_attachment(sender, to, subject, message_text, csv)

    # send message
    send_message(service=service, user_id='me', message=message)


def _create_sending_csv(mode, columns):
    selected_csv = BASE_PATH + '/data/selected/selected.csv'
    old_selected_csv = BASE_PATH + '/data/selected/old_selected.csv'
    sending_csv = BASE_PATH + '/data/sending/column_filtered.csv'
    # 新規物件を抽出
    if mode == 'new':
        df = pd.read_csv(selected_csv)
        old_df = pd.read_csv(old_selected_csv)
        new_df = df[-df['room_id'].isin(old_df['room_id'])]
        new_df.to_csv(sending_csv, sep = ',', encoding='utf-8', columns=columns)
    else:
        df = pd.read_csv(selected_csv)
        df.to_csv(sending_csv, sep = ',', encoding='utf-8', columns=columns) 

    return sending_csv


# mode: new or all
def send_data(mode, columns):
    # 件名
    subject = "最新データ（差分）" if mode == 'new' else "最新データ（すべて）"

    # 送信用csvを生成
    sending_csv = _create_sending_csv(mode, columns) 
    # 送信
    _send_csv(subject, "", sending_csv)



