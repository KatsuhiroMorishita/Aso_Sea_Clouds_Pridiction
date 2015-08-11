#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: create_learning_data
# purpose: 雲海の出現予想に必要な特徴量を作成する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
#地点A　阿蘇山頂, 地点B　阿蘇乙姫
import datetime
import feature
import copy
import random
import timeKM

# 処理の対象期間
date_start = datetime.datetime(2005, 3, 10)
date_end   = datetime.datetime(2013, 8, 1)


def get_unkai(_date, unkai_list):
	""" 当日に雲海が出たかどうかのフラグ
	該当するなら、数字の1を返す。
	"""
	if _date in unkai_list:
		return 1
	else:
		return 0


def get_unkai_pre1(_date, unkai_list):
	""" 当日の翌日朝に雲海が出たかどうかのフラグ
	該当するなら、数字の2を返す。
	"""
	_date += datetime.timedelta(days=1)
	if _date in unkai_list:
		return 2
	else:
		return 0


def get_unkai_pre2(_date, unkai_list):
	""" 当日の翌々日朝に雲海が出たかどうかのフラグ
	該当するなら、数字の4を返す。
	"""
	_date += datetime.timedelta(days=2)
	if _date in unkai_list:
		return 4
	else:
		return 0


# 気象データの読み込み
weather_data_Aso = feature.read_weather_data("fusion_aso.csv", len(feature.index_A))
weather_data_Otohime = feature.read_weather_data("fusion_asoOtohime.csv", len(feature.index_B))
#print(weather_data_Aso)
#print(weather_data_Otohime)


# 雲海の出た日付けのリストを読み込む
unkai_date_list = []
with open("unkai_date.csv", "r", encoding="utf-8-sig") as fr:
	lines = fr.readlines()
	for line in lines:
		line = line.rstrip()
		date = line + " 0:0:0"
		t = timeKM.getTime(date)
		unkai_date_list.append(t)
#print(unkai_date_list)


# 教師データを作る
unkai_good = []
unkai_bad= []
#unkai_label = ["st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7"]
unkai_label = ["st0", "st1"]
_date = date_start + datetime.timedelta(days=4)
while _date <= date_end:
	#print(_date)
	_feature = feature.create_feature(_date, weather_data_Aso, weather_data_Otohime)
	#print(_feature)
	if _feature != None:
		unkai_point = get_unkai(_date, unkai_date_list)# + get_unkai_pre1(_date, unkai_date_list) + get_unkai_pre2(_date, unkai_date_list)
		_unkai = unkai_label[unkai_point]
		one_teaching_data = _feature + [_unkai]
		if _unkai == "st0":
			unkai_bad.append((_date, one_teaching_data)) # 時刻と一緒にタプルで保存
		else:
			unkai_good.append((_date, one_teaching_data))
		#print(_date, one_teaching_data)
	_date += datetime.timedelta(days=1)

# 雲海が出たデータ数と、出なかったデータ数を揃える
teaching_data = copy.copy(unkai_good)
use_amount = int(len(unkai_good) * 1.0)
if len(unkai_bad) < use_amount:     # 雲海の出現日数よりも非出現日数が少ない場合、非出現データは全て使う
	use_amount = len(unkai_bad)     # ただし、本気でやるなら偽陽性・偽陰性の許容量に合わせて教師データ数は決めるべき
for _ in range(use_amount):
	i = random.randint(0, use_amount - 1)
	new_member = unkai_bad.pop(i)
	teaching_data.append(new_member)
#print(teaching_data)


# 教師データをファイルに保存
if len(teaching_data) > 0:
	with open("teaching_data.csv", "w", encoding="utf-8") as fw:
		length = len(teaching_data[0][1])             # 要素数を把握
		fw.write("date,")
		label = ["V" + str(i) for i in range(length)] # ラベル
		fw.write(",".join(label))
		fw.write("\n")
		for _date, one_teaching_data in teaching_data:
			one_teaching_data = [str(x) for x in one_teaching_data]
			one_teaching_data = ",".join(one_teaching_data)
			fw.write(str(_date) + ",")
			fw.write(one_teaching_data)
			fw.write("\n")

