# coding: utf-8

from bs4 import BeautifulSoup
import pandas as pd
from pandas import Series, DataFrame


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
def get_walk(val):
    if '歩' in val:
        return get_num(val)
    else:
        return 99


def get_near_info(nears):
    res = [''] * 6 # near, walk, near, walk, near, walk
    if len(nears) >= 1 and nears[0] != '':
        res[0] = nears[0].split(' ')[0]
        res[1] = get_walk(nears[0].split(' ')[1])
    if len(nears) >= 2 and nears[1] != '':
        res[2] = nears[1].split(' ')[0]
        res[3] = get_walk(nears[1].split(' ')[1])
    if len(nears) >= 3 and nears[2] != '':  
        res[4] = nears[2].split(' ')[0]
        res[5] = get_walk(nears[2].split(' ')[1])

    return res


def create_data_frame(typ, name, address, near1, near2, near3, walk1, walk2, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link):
    df = pd.DataFrame()
    df['building_type'] = Series(typ)
    df['building_name'] = Series(name)
    df['address'] = Series(address)
    df['near1'] = Series(near1)
    df['walk1'] = Series(walk1)
    df['near2'] = Series(near2)
    df['walk2'] = Series(walk2)
    df['near3'] = Series(near3)
    df['walk3'] = Series(walk3)
    df['age'] = Series(age)
    df['height'] = Series(height)
    df['office'] = Series(office)
    df['commute'] = Series(commute)
    df['change'] = Series(change)
    df['floor'] = Series(floor)
    df['rent'] = Series(rent)
    df['admin'] = Series(admin)
    df['deposite'] = Series(shikikin)
    df['reward'] = Series(reikin)
    df['room_plan'] = Series(floor_plan)
    df['area'] = Series(area)
    df['link'] = Series(detail_link)

    return df

"""
def create_data_frame(typ, name, address, near1, near2, near3, walk1, walk2, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link):
    typ = Series(typ)
    name = Series(name)
    address = Series(address)
    near1 = Series(near1)
    walk1 = Series(walk1)
    near2 = Series(near2)
    walk2 = Series(walk2)
    near3 = Series(near3)
    walk3 = Series(walk3)
    age = Series(age)
    height = Series(height)
    office = Series(office)
    commute = Series(commute)
    change = Series(change)
    floor = Series(floor)
    rent = Series(rent)
    admin = Series(admin)
    shikikin = Series(shikikin)
    reikin = Series(reikin)
    floor_plan = Series(floor_plan)
    area = Series(area)
    detail_link = Series(detail_link)

    df = pd.concat([typ, name, address, near1, walk1, near2, walk2, near3, walk3, age, height, office, commute, change, floor, rent, admin, shikikin, reikin, floor_plan, area, detail_link])

    return df
"""