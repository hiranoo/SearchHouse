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
from base_path import *


# BeautifulSoup objectを作成
def create_html_object(url):
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, features="html.parser")
    time.sleep(2) # scraping manner, sleep 2 sec
    return soup

# 一つの建物について、各種データを引数のリストに格納する
def fetch_cassetteitem_data(item, typ, name, address, near1, near2, near3, walk1, walk2, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link):
    # 全部屋共通のデータを取得
    _typ = get_value(item.find("span", {'class':'ui-pct ui-pct--util1'}))  # 建物種別
    _name = get_name(get_value(item.find("div",{'class':'cassetteitem_content-title'})))  #マンション名
    _address = get_value(item.find("li",{'class':'cassetteitem_detail-col1'}))  #住所
    _nears = get_value(item.find_all("div",{'class':'cassetteitem_detail-text'}))  #物件の最寄り駅情報
    _near1, _walk1, _near2, _walk2, _near3, _walk3, = get_near_info(_nears)  #最寄り駅, 徒歩分（3つ）
    _age, _height = get_value(item.find("li",{'class':'cassetteitem_detail-col3'}).find_all("div"))  #築年数, 高さ
    _commute = get_value(item.find("ul",{'class':'cassetteitem_transfer-list'}).find("li"))  #officeの最寄り駅情報
    _office, _commute, _change = get_commute_value(_commute)  # office最寄り駅, 通勤時間, 乗換回数

    # 部屋ごとのデータを取得
    tbodies = item.find_all('tbody')  # 部屋情報
    for tbody in tbodies:
        objects = tbody.find("tr", {'class':'js-cassette_link'}).find_all("td")
        _floor = get_value(objects[2])
        _rent, _admin = get_value(objects[3].find_all("li"))
        _shikikin, _reikin = get_value(objects[4].find_all("li"))
        _floor_plan, _area = get_value(objects[5].find_all("li"))
        _detail_link = "https://suumo.jp" + str(objects[8]).split("href=\"")[1].split("\" ")[0]

        # 取得したデータを引数のリストに格納
        typ.append(_typ)
        name.append(_name)
        address.append(_address)
        near1.append(_near1)
        walk1.append(_walk1)
        near2.append(_near2)
        walk2.append(_walk2)
        near3.append(_near3)
        walk3.append(_walk3)
        age.append(get_num(_age))
        height.append(get_num(_height))
        office.append(_office)
        commute.append(_commute)
        change.append(_change)
        floor.append(get_num(_floor))
        rent.append(get_num(_rent))
        admin.append(get_num(_admin))
        shikikin.append(get_num(_shikikin))
        reikin.append(get_num(_reikin))
        floor_plan.append(_floor_plan)
        area.append(get_num(_area.split('m')[0]))
        detail_link.append(_detail_link)


#
# 取得したデータをcsvファイルに保存する
#
def fetch_basic_data():
    # 閲覧する検索条件の urlリストを取得
    output_name_list = []
    url_list = []
    f = open(BASE_PATH + '/url_list.txt', 'r')
    for val in f.read().split('\n'):
        if 'output_name=' in val:
            output_name_list.append(val.replace('output_name=', ''))
        elif 'url=' in val:
            url_list.append(val.replace('url=', ''))
    
    # 検索条件の数
    search_condition_num = len(url_list)

    # 実行日
    ima = datetime.datetime.now()

    # ひとつひとつの検索条件について、全ページを舐める
    for i in range(search_condition_num):
        # 出力csvファイル
        output_name = BASE_PATH + "/data/fetched/" + output_name_list[i] + "_{}.csv".format(ima.strftime("%Y%m%d"))
        # 検索条件のurl
        url = url_list[i]

        # ページ数を算出
        soup = create_html_object(url)
        pages_num = get_num(get_value(soup.find_all("ol", {'class':'pagination-parts'})[0].find_all("a")[-1]))

        # 全ページ分のurlを作成
        urls = [''] * pages_num
        for page_num in range(pages_num):
            urls[page_num] = url if page_num == 0 else url + '&pn={}'.format(page_num)

        # 取得するデータリストを宣言
        typ = [] # 賃貸マンション、賃貸アパートなど
        name = [] #マンション名
        address = [] #住所
        near1 = [] #立地1つ目（最寄駅/徒歩~分）
        near2 = [] #立地2つ目（最寄駅/徒歩~分）
        near3 = [] #立地3つ目（最寄駅/徒歩~分）
        walk1 = [] #立地1つ目（最寄駅/徒歩~分）
        walk2 = [] #立地2つ目（最寄駅/徒歩~分）
        walk3 = [] #立地3つ目（最寄駅/徒歩~分）
        age = [] #築年数
        height = [] #建物高さ
        office = [] # 六本木一丁目駅
        commute = [] # N 分
        change = [] # N 回
        floor = [] #階
        rent = [] #賃料
        admin = [] #管理費
        shikikin = [] #敷金
        reikin = [] #礼金
        floor_plan = [] #間取り
        area = [] #専有面積
        detail_link = [] #詳細を見るのリンク

        # 各ページについて、物件データを取得していく
        for url in urls:
            soup = create_html_object(url)
            summary = soup.find("div",{'id':'js-bukkenList'})
            # casseteitem = 建物ごとの物件リスト
            cassetteitems = summary.find_all("div",{'class':'cassetteitem'})

            #各cassetteitemに対し、各種データを取得する
            for item in cassetteitems:
                fetch_cassetteitem_data(item, typ, name, address, near1, near2, near3, walk1, walk2, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link)

        # リストからDataFrameを作成
        suumo_df = create_data_frame(typ, name, address, near1, near2, near3, walk1, walk2, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link)

        #csvファイルとして保存
        suumo_df.to_csv(output_name, sep = ',',encoding='utf-8')
