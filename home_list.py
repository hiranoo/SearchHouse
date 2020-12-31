# coding: utf-8

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import datetime
import time
import re
import sys

# BeautifulSoup object からhtmlタグなしの値を取り出す
def get_value(obj):
    if str(type(obj)) == "<class 'bs4.element.ResultSet'>":
        res = []
        for item in obj:
            res.append(item.get_text(strip=True))
        return res
    elif str(type(obj)) == "<class 'bs4.element.Tag'>":
        res = obj.get_text(strip=True)
        return res
    else:
        return

def get_commute_value(com):
    com = com.split(')')[1]
    station, time = com.split('（')
    time, num = time.split('分・')
    num = num.split('回')[0]
    return [station, int(time), int(num)]

# マンション名が駅名築年数とかなら、空白にする
def get_name(name):
    if '駅' in name and '築' in name and '年' in name:
        return ''
    else: 
        return name

# 数値（整数、小数)を取り出す
def get_num(string):
    string = string.replace(',', '')
    _float = []
    _int = []
    _float = re.findall("\d+\.\d+", string)
    _int = re.findall("\d+", string)
    if len(_float) > 0:
        if '万' in string:
            return float(_float[0])*10000
        else:
            return float(_float[0])
    elif len(_int) > 0:
        if '万' in string:
            return int(_int[0])*10000
        else:
            return int(_int[0])
    else:
        return 0

# 徒歩分を取り出す
def get_walk(location):
    # locationが''のとき
    if location == '':
        return ''
    val = location.split(' ')[1]
    val = 99 if val == '' else val
    if '歩' in val:
        return get_num(val)
    else:
        return 99

if __name__ == '__main__':
    # url list を読み込む
    output_name_list = []
    url_list = []
    f = open('url_list.txt', 'r')
    for val in f.read().split('\n'):
        if 'output_name=' in val:
            output_name_list.append(val.replace('output_name=', ''))
        elif 'url=' in val:
            url_list.append(val.replace('url=', ''))

    ima = datetime.datetime.now()

    
    for i in range(len(url_list)):
        output_name = "./data/" + output_name_list[i] + "_{}{}{}.csv".format(ima.year, ima.month, ima.day)
        url = url_list[i]
        
        #データ取得
        result = requests.get(url)
        c = result.content

        #HTMLを元に、オブジェクトを作る
        soup = BeautifulSoup(c, features="html.parser")

        #物件リストの部分を切り出し
        summary = soup.find("div",{'id':'js-bukkenList'})

        #ページ数を取得
        pages_num = get_num(get_value(soup.find_all("ol", {'class':'pagination-parts'})[0].find_all("a")[-1]))
        
        #URLを入れるリスト
        urls = []

        #1ページ目を格納
        urls.append(url)

        #2ページ目から最後のページまでを格納
        for i in range(pages_num-1):
            pg = str(i+2)
            url_page = url + '&pn=' + pg
            urls.append(url_page)

        typ = [] # 賃貸マンション、賃貸アパートなど
        name = [] #マンション名
        address = [] #住所
        location0 = [] #立地1つ目（最寄駅/徒歩~分）
        location1 = [] #立地2つ目（最寄駅/徒歩~分）
        location2 = [] #立地3つ目（最寄駅/徒歩~分）
        location_walk0 = [] #立地1つ目（最寄駅/徒歩~分）
        location_walk1 = [] #立地2つ目（最寄駅/徒歩~分）
        location_walk2 = [] #立地3つ目（最寄駅/徒歩~分）
        age = [] #築年数
        height = [] #建物高さ
        commute_station = [] # 六本木一丁目駅
        commute_time = [] # N 分
        commute_change_num = [] # N 回
        floor = [] #階
        rent = [] #賃料
        admin = [] #管理費
        shikikin = [] #敷金
        reikin = [] #礼金
        floor_plan = [] #間取り
        area = [] #専有面積
        detail_link = [] #詳細を見るのリンク
        cnt = 0

        #各ページで以下の動作をループ
        for url in urls:
            #物件リストを切り出し
            result = requests.get(url)
            c = result.content
            soup = BeautifulSoup(c)
            summary = soup.find("div",{'id':'js-bukkenList'})

            cassetteitems = summary.find_all("div",{'class':'cassetteitem'})

            #各cassetteitemに対し、以下の動作をループ
            for item in cassetteitems:
                #各建物から売りに出ている部屋数を取得
                tbodies = item.find_all('tbody')

                #マンション名取得
                _name = get_value(item.find("div",{'class':'cassetteitem_content-title'}))

                #住所取得
                _address = get_value(item.find("li",{'class':'cassetteitem_detail-col1'}))

                #立地を取得
                _locations = get_value(item.find_all("div",{'class':'cassetteitem_detail-text'}))

                #築年数, 高さ
                _age, _height = get_value(item.find("li",{'class':'cassetteitem_detail-col3'}).find_all("div"))

                # 通勤時間
                _commute = get_value(item.find("ul",{'class':'cassetteitem_transfer-list'}).find("li"))
                _commute_station, _commute_time, _commute_change_num = get_commute_value(_commute)
            
                # 以下、部屋ごとにデータ取得
                for tbody in tbodies:
                    objects = tbody.find("tr", {'class':'js-cassette_link'}).find_all("td")
                    _floor = get_value(objects[2])
                    _rent, _admin = get_value(objects[3].find_all("li"))
                    _shikikin, _reikin = get_value(objects[4].find_all("li"))
                    _floor_plan, _area = get_value(objects[5].find_all("li"))
                    _detail_link = "https://suumo.jp" + str(objects[8]).split("href=\"")[1].split("\" ")[0]

                    # データを登録
                    name.append(get_name(_name))
                    address.append(_address)

                    if len(_locations) == 0:
                        location0.append("")
                        location1.append("")
                        location2.append("")
                    elif len(_locations) == 1:
                        location0.append(_locations[0].split(' ')[0])
                        location1.append("")
                        location2.append("")
                    elif len(_locations) == 2:
                        location0.append(_locations[0].split(' ')[0])
                        location1.append(_locations[1].split(' ')[0])
                        location2.append("")
                    elif len(_locations) == 3:
                        location0.append(_locations[0].split(' ')[0])
                        location1.append(_locations[1].split(' ')[0])
                        location2.append(_locations[2].split(' ')[0])
                        location_walk0.append(get_walk(_locations[0]))
                        location_walk1.append(get_walk(_locations[1]))
                        location_walk2.append(get_walk(_locations[2]))
                    
                    age.append(get_num(_age))
                    height.append(get_num(_height))
                    commute_station.append(_commute_station)
                    commute_time.append(_commute_time)
                    commute_change_num.append(_commute_change_num)
                    floor.append(get_num(_floor))
                    rent.append(get_num(_rent))
                    admin.append(get_num(_admin))
                    shikikin.append(get_num(_shikikin))
                    reikin.append(get_num(_reikin))
                    floor_plan.append(_floor_plan)
                    area.append(get_num(_area.split('m')[0]))
                    detail_link.append(_detail_link)
                    
            #プログラムを10秒間停止する（スクレイピングマナー）
            time.sleep(10)

        #各リストをシリーズ化
        name = Series(name)
        address = Series(address)
        location0 = Series(location0)
        location1 = Series(location1)
        location2 = Series(location2)
        location_walk0 = Series(location_walk0)
        location_walk1 = Series(location_walk1)
        location_walk2 = Series(location_walk2)
        age = Series(age)
        height = Series(height)
        commute_station = Series(commute_station)
        commute_time = Series(commute_time, dtype='int8')
        commute_change_num = Series(commute_change_num, dtype='int8')
        floor = Series(floor)
        rent = Series(rent)
        admin = Series(admin)
        shikikin = Series(shikikin)
        reikin = Series(reikin)
        floor_plan = Series(floor_plan)
        area = Series(area)
        detail_link = Series(detail_link)

        #各シリーズをデータフレーム化
        suumo_df = pd.concat([name, address, location0, location_walk0, location1, location_walk1, location2, location_walk2, age, height, commute_station, commute_time, commute_change_num, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link], axis=1)

        #カラム名
        suumo_df.columns=['building_name','address','nearest1', 'walk1', 'nearest2', 'walk2', 'nearest3', 'walk3', 'age','height', 'office', 'commute', 'change', 'floor','rent','admin', 'deposit', 'reward','room_plan','area', 'link']

        #csvファイルとして保存
        suumo_df.to_csv(output_name, sep = ',',encoding='utf-8')