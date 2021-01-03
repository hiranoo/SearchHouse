# coding: utf-8

import datetime
import glob
import os
import shutil

import pandas as pd
from pandas import DataFrame, Series
from fetch_data import *
from process_data import *
from base_path import *


def _get_data_from_link(link_series):
    num = len(link_series)

    # 方角, 取扱店舗物件コード, 入居可能日, 総戸数, 間取り詳細 を取得
    directions = [''] * num
    room_ids = [''] * num
    availables = [''] * num
    totals = [''] * num
    detail_room_plans = [''] * num

    for i, detail_url in enumerate(link_series):
        soup = create_html_object(detail_url)
        view_elements = soup.find("table", {'class':'property_view_table'}).find_all("tr")
        abstract_elements = soup.find("table", {'class':'data_table table_gaiyou'}).find_all("tr")

        directions[i] = get_value(view_elements[4].find_all("td")[0])
        room_ids[i] = get_value(abstract_elements[4].find_all("td")[1])
        availables[i] = get_value(abstract_elements[3].find_all("td")[0])
        total = get_value(abstract_elements[5].find_all("td")[1])
        totals[i] = int(total.split('戸')[0]) if '戸' in total else -1
        detail_room_plans[i] = get_value(abstract_elements[0].find_all("td")[0])

    directions = Series(directions)
    room_ids = Series(room_ids)
    availables = Series(availables)
    totals = Series(totals)

    return (directions, room_ids, availables, totals, detail_room_plans)


def _before_detail_filter(df):
    d_age_t = df['age'] <= 20
    d_age_b = df['age'] > 0
    d_walk1 = df['walk1'] <= 15
    d_floor = df['height'] > df['floor']
    d_money = df['monthly'] <= 70000
    d_change = df['change'] <= 3
    d_area = df['area'] >= 23
    d_nearest1 = -df['near1'].str.contains('舎人ライナー')

    return df[d_age_t * d_age_b * d_walk1 * d_floor * d_money * d_change * d_area * d_nearest1]


def _add_data(df):
    directions, room_ids, availables, totals, detail_room_plans = _get_data_from_link(df['link'])
    df['direction'] = directions
    df['room_id'] = room_ids
    df['available_date'] = availables
    df['total'] = totals
    df['detail_room_plan'] = detail_room_plans
    return df


def _after_detail_filter(df):
    #取扱店舗物件コードが重複する行を削除（suumoでは別物件として記載されているが実際は同一物件だから）
    df.drop_duplicates(subset=['room_id', 'address', 'age', 'height', 'floor', 'area'],inplace=True)

    # 希望条件
    d_direction = -df['direction'].str.contains('-|北|西')
    d_available_date = df['available_date'].str.contains('即|1月|2月')

    return df[d_direction * d_available_date]


def _save_selected_data(df):
    # selected.csvをold_selected.csvに変換
    selected_csv = BASE_PATH + '/data/selected/selected.csv'
    old_selected_csv = BASE_PATH + '/data/selected/old_selected.csv'
    if os.path.exists(selected_csv):
        shutil.copy(selected_csv, old_selected_csv)

    # save df as a csv file
    df.to_csv(BASE_PATH + '/data/selected/selected.csv', sep = ',',encoding='utf-8')


def select_and_save_data():
    # ../data/latest/fname.csv を合算して DataFrame に
    files = glob.glob(BASE_PATH + '/data/latest/*.csv')
    df = pd.DataFrame()
    for i, fil in enumerate(files):
        add_df = pd.read_csv(fil)
        if i == 0:
            df = add_df
        else:
            df = pd.concat([df, add_df])

    # 月額を生成
    df['monthly'] = df['rent'] + df['admin']

    # 1st filter (詳細画面を検索するデータに絞る)
    df = _before_detail_filter(df)
    # フィルタリング後はDataFrameのindexが連番ではなくなるので、連番に戻す
    df.index = range(len(df))

    # 詳細画面を検索してデータを追加
    df = _add_data(df)

    # 2nd filter (好みの条件に絞る)
    df = _after_detail_filter(df)
    # フィルタリング後はDataFrameのindexが連番ではなくなるので、連番に戻す
    df.index = range(len(df))

    # save
    _save_selected_data(df)
    
