#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: feature
# purpose: 雲海出現を予測するために必要な特徴量を作成する
# memo: 平均や積算の関数を用意するともう少し整理できるなぁ。
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
#地点A　阿蘇山頂, 地点B　阿蘇乙姫
import datetime
import numpy as np
from datetime import datetime as dt
from datetime import timedelta as td
import math
import copy
import re
import timeKM


index_B = {"時刻":0, "降水量":1, "気温":2, "風速":3, "風向":4, "日照時間":5}#, "降雪":6, "積雪":7}
index_A = {"時刻":0, "現地気圧":1, "海面気圧":2, "降水量":3, "気温":4, "露点温度":5, "蒸気圧":6, "湿度":7, "風速":8, "風向":9, "日照時間":10, "全天日射量":11, "降雪":12, "積雪":13, "天気":14, "雲量":15, "視程":16}


def get_season(_date):
	""" 日付けをシーズン化したもの
	"""
	return int((_date - datetime.datetime(_date.year, 1, 1)).total_seconds() / (7 * 24 * 3600))


def get_measurement_value(_date, data_set, target_index):
	""" 指定日時の観測値を返す
	"""
	weather_data, _index = data_set
	one_data = weather_data[_date]
	if one_data == None:
		return
	value = one_data[_index[target_index]]
	if target_index == "風向":
		if value != None and value != 0.0: # valueには方位が入っているはず
			label = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東", "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西", "静穏"]
			value = label.index(value)#int(label.index(direction) / 4)
		else:
			value = None
	return value


def get_diff(time1, time2, data_set, target_index):
	""" 2つの時刻間の差分を取る
	"""
	v1 = get_measurement_value(time1, data_set, target_index)
	v2 = get_measurement_value(time2, data_set, target_index)
	if v1 is None or v2 is None:
		return None
	else:
		return v1 - v2

def minus(v1, v2):
	""" ２つの値の差分を返す
	"""
	if v1 is None or v2 is None:
		return None
	else:
		return v1 - v2


def get_diff2(time, data_set1, data_set2, target_index):
	""" 2つのデータセット間の差分を取る
	"""
	v1 = get_measurement_value(time, data_set1, target_index)
	v2 = get_measurement_value(time, data_set2, target_index)
	if v1 is None or v2 is None:
		return None
	else:
		return v1 - v2



def get_values(origin_time, data_set, key, term_hours=range(1, 25)):
	""" origin_timeからterm_hoursで指定した時間前の観測データをリストとして返す
	"""
	weather_data, _index = data_set
	values = []
	for i in term_hours:
		__date = origin_time - td(hours=i)
		if __date not in weather_data:
			values.append(None)
			continue
		one_data = weather_data[__date]
		#print(one_data)
		if one_data == None:
			values.append(None)
			continue
		values.append(one_data[_index[key]])
	#print(values)
	return values


def get_average(origin_time, data_set, key, term_hours=range(0, 24), remove=["休止中", "#", None]):
	""" 観測値の平均を返す
	"""
	values = get_values(origin_time, data_set, key, term_hours)
	_values = []
	for val in values:
		if val in remove:
			continue
		_values.append(val)
	if len(_values) == 0:
		return None
	else:
		return sum(_values) / float(len(_values))


def get_someone(origin_time, data_set, key, term_hours, func):
	""" 観測値の平均を返す
	"""
	values = get_values(origin_time, data_set, key, term_hours)
	_values = []
	for val in values:
		if val in ["休止中", "#", None]:
			continue
		_values.append(val)
	if len(_values) == 0:
		return None
	else:
		return func(_values)


def get_TTd(_date, hour, data_set):
	""" 前日のhour時における湿数を返す
	"""
	weather_data, _index = data_set
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data[_date]
	if one_data == None:
			return
	T = one_data[_index["気温"]]
	Td = one_data[_index["露点温度"]]
	TTd = None
	if T != None and Td != None:
		TTd = T - Td
	return TTd





def get_weather_dict(lines):
	""" 気象データの辞書を返す
	"""
	weather_dict = {}

	# 引数の検査
	if len(lines) == 0:
		return {}

	# 要素数（エラーを排除するのに使う）を推定
	sizes = [0] * 50
	loop = 50
	if len(lines) < loop:
		loop = len(lines)
	for i in range(loop):
		field = lines[i].split(",")
		if len(field) > len(sizes):
			print("--size over on read_weather_data()--")
		sizes[len(field)] += 1                     # エラーが出て止まってくれたほうがいいと思う・・・
	th = sizes.index(max(sizes)) - 1               # 最初のフィールドには時刻が入っているはずで、これはカウントしないので1を引く
	#print("th: ", th)

	# 観測値にバラす
	for line in lines:
		#print(line)
		line = line.rstrip()
		if "時" in line:
			continue
		field = line.split(",")
		t = field[0]
		t = timeKM.getTime(t)
		field = field[1:]
		new_field = []
		for mem in field:
			#print(mem)
			if "東" in mem or "西" in mem or "南" in mem or "北" in mem:
				mem = re.sub(" |　|[)]", "", mem)
			fuga = mem.replace(".", "")
			fuga = fuga.replace(" )", "")            # 観測上のおかしなデータにくっつく記号
			#if len(fuga) > 0:
			#	if "-" == fuga[0]:
			#		fuga = fuga[1:]
			fuga = fuga.replace("-", "")             # -10, 10-　みたいなパターン。数値の前のマイナス符号があれば負値。
			fuga = fuga.replace("+", "")             # +10, 10+　みたいなパターン。
			if fuga.isdigit() == True:
				mem = mem.replace(" )", "")
				if "-" == mem[-1] or "+" == mem[-1]: # 10-, 10+　みたいなパターンへの対応
					mem = mem[:-1]
				new_field.append(float(mem))
			else:
				if mem == "" or mem == "--":
					new_field.append(0.0)
				elif mem == "×" or mem == "///":     # 恐らく、非観測項目にくっつく記号
					new_field.append(None)
				else:
					new_field.append(mem)
		#exit()
		#print(new_field)
		if len(new_field) >= th:
			weather_dict[t] = new_field
		else:
			weather_dict[t] = None
	return weather_dict


def read_weather_data(fpath):
	""" 気象データをファイルから読み込む
	"""
	weather_data = {}
	with open(fpath, "r", encoding="utf-8-sig") as fr:
		print("--AMeDAS data reading--", fpath)
		lines = fr.readlines()
		if len(lines) == 0:
			return {}
		#print(str(lines[0:100]))
		weather_data = get_weather_dict(lines)
	return weather_data


def load_weather_library(ids):
	""" ファイルから観測データを読みだす
	"""
	weather_library = {}
	for _id in ids:
		fname = "amedas_" + _id + ".csv"
		weather_data = read_weather_data(fname)
		#print(len(weather_data))
		index = index_B
		if int(_id) > 47000:  # 現時点では問題ないが、indexは少なくとも3種類あるので全国展開時には注意が必要。
			index = index_A
		weather_library[_id] = [weather_data, copy.copy(index)]
	return weather_library


def create_feature23(_date, weather_library):
	""" 23時時点での予想を実施する特徴ベクトルを作る
	"""
	print("23:00, feature of ", _date)
	weather_kumamoto = weather_library["47819"]
	weather_asootohime = weather_library["1240"]
	weather_unzendake = weather_library["47818"]
	weather_shimabara = weather_library["0962"]
	#print(str(weather_kumamoto[_date]))
	pre_date = _date - td(days=1)
	y, m, d = pre_date.year, pre_date.month, pre_date.day
	_feature = []
	_feature += [get_season(_date)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 23), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 23), weather_asootohime, "気温")]
	_feature += [get_diff2(dt(y, m, d, 23), weather_unzendake, weather_shimabara, "気温")]
	_feature += [get_average(dt(y, m, d, 23), weather_asootohime, "気温", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 23), weather_asootohime, "降水量", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 23), weather_asootohime, "降水量", range(0, 24))]
	_feature += [get_average(dt(y, m, d, 23), weather_asootohime, "日照時間", range(0, 24))]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_unzendake, "風速")]
	_feature += [get_average(dt(y, m, d, 23), weather_asootohime, "風速", range(1, 3))]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_kumamoto, "露点温度")]
	_feature += [get_TTd(_date, 14, weather_kumamoto)]
	_feature += [get_TTd(_date, 23, weather_kumamoto)]
	_feature += [get_TTd(_date, 14, weather_unzendake)]
	_feature += [get_TTd(_date, 23, weather_unzendake)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "蒸気圧")]
	_feature += [get_diff(dt(y, m, d, 22), dt(y, m, d, 23), weather_kumamoto, "現地気圧")]
	_feature += [minus(get_average(dt(y, m, d, 23), weather_unzendake, "現地気圧", range(0, 72)), get_measurement_value(dt(y, m, d, 23), weather_unzendake, "現地気圧"))]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "湿度")]
	_feature += [get_measurement_value(dt(y, m, d,  6) - td(days=1), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_unzendake, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_kumamoto, "雲量")]
	#print("fuga")
	_feature = [-math.e if x == None else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "休止中" else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "#" else x for x in _feature] # 欠損値を-eに置換
	#print(_feature)
	return np.array(_feature)



def create_feature16(_date, weather_library):
	""" 16時時点での予想を実施する特徴ベクトルを作る
	_date: 予報対象日
	"""
	print("16:00, feature of ", _date)
	weather_kumamoto = weather_library["47819"]
	weather_asootohime = weather_library["1240"]
	weather_unzendake = weather_library["47818"]
	weather_shimabara = weather_library["0962"]
	pre_date = _date - td(days=1)
	y, m, d = pre_date.year, pre_date.month, pre_date.day
	_feature = []
	_feature += [get_season(_date)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 16), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 16), weather_asootohime, "気温")]
	_feature += [get_diff2(dt(y, m, d, 16), weather_unzendake, weather_shimabara, "気温")]
	_feature += [get_average(dt(y, m, d, 16), weather_asootohime, "気温", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 16), weather_asootohime, "降水量", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 16), weather_asootohime, "降水量", range(0, 24))]
	_feature += [get_average(dt(y, m, d, 16), weather_asootohime, "日照時間", range(0, 12))]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_unzendake, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_unzendake, "風向")]

	_feature += [get_someone(dt(y, m, d, 16), weather_asootohime, "風速", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 16), weather_asootohime, "気温", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 16), weather_unzendake, "風速", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 16), weather_unzendake, "気温", range(0, 6), max)]

	_feature += [get_average(dt(y, m, d, 16), weather_asootohime, "風速", range(1, 3))]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "現地気圧")]
	_feature += [get_TTd(_date, 14, weather_kumamoto)]
	_feature += [get_TTd(_date, 16, weather_kumamoto)]
	_feature += [get_TTd(_date, 14, weather_unzendake)]
	_feature += [get_TTd(_date, 16, weather_unzendake)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "蒸気圧")]
	_feature += [get_diff(dt(y, m, d, 15), dt(y, m, d, 16), weather_kumamoto, "現地気圧")]
	_feature += [minus(get_average(dt(y, m, d, 16), weather_unzendake, "現地気圧", range(0, 72)), get_measurement_value(dt(y, m, d, 16), weather_unzendake, "現地気圧"))]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "湿度")]
	_feature += [get_measurement_value(dt(y, m, d,  6) - td(days=1), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_unzendake, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_kumamoto, "雲量")]
	#print("fuga")
	_feature = [-math.e if x == None else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "休止中" else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "#" else x for x in _feature] # 欠損値を-eに置換
	#print(_feature)
	return np.array(_feature)



def create_feature18(_date, weather_library):
	""" 18時時点での予想を実施する特徴ベクトルを作る
	16時と性能差があまりない。
	_date: 予報対象日
	"""
	print("16:00, feature of ", _date)
	weather_kumamoto = weather_library["47819"]
	weather_asootohime = weather_library["1240"]
	weather_unzendake = weather_library["47818"]
	weather_shimabara = weather_library["0962"]
	pre_date = _date - td(days=1)
	y, m, d = pre_date.year, pre_date.month, pre_date.day
	_feature = []
	_feature += [get_season(_date)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 18), weather_kumamoto, "気温")]
	_feature += [get_diff(dt(y, m, d, 14), dt(y, m, d, 18), weather_asootohime, "気温")]
	_feature += [get_diff2(dt(y, m, d, 18), weather_unzendake, weather_shimabara, "気温")]
	_feature += [get_average(dt(y, m, d, 18), weather_asootohime, "気温", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 18), weather_asootohime, "降水量", range(0, 72))]
	_feature += [get_average(dt(y, m, d, 18), weather_asootohime, "降水量", range(0, 24))]
	_feature += [get_average(dt(y, m, d, 18), weather_asootohime, "日照時間", range(0, 12))]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_unzendake, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_unzendake, "風向")]

	_feature += [get_someone(dt(y, m, d, 18), weather_asootohime, "風速", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 18), weather_asootohime, "気温", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 18), weather_unzendake, "風速", range(0, 6), max)]
	_feature += [get_someone(dt(y, m, d, 18), weather_unzendake, "気温", range(0, 6), max)]

	_feature += [get_average(dt(y, m, d, 18), weather_asootohime, "風速", range(1, 3))]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_kumamoto, "現地気圧")]
	_feature += [get_TTd(_date, 14, weather_kumamoto)]
	_feature += [get_TTd(_date, 18, weather_kumamoto)]
	_feature += [get_TTd(_date, 14, weather_unzendake)]
	_feature += [get_TTd(_date, 18, weather_unzendake)]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_kumamoto, "蒸気圧")]
	_feature += [get_diff(dt(y, m, d, 15), dt(y, m, d, 18), weather_kumamoto, "現地気圧")]
	_feature += [minus(get_average(dt(y, m, d, 18), weather_unzendake, "現地気圧", range(0, 72)), get_measurement_value(dt(y, m, d, 18), weather_unzendake, "現地気圧"))]
	_feature += [get_measurement_value(dt(y, m, d, 18), weather_kumamoto, "湿度")]
	_feature += [get_measurement_value(dt(y, m, d,  6) - td(days=1), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_unzendake, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21) - td(days=1), weather_kumamoto, "雲量")]
	#print("fuga")
	_feature = [-math.e if x == None else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "休止中" else x for x in _feature] # 欠損値を-eに置換
	_feature = [-math.e if x == "#" else x for x in _feature] # 欠損値を-eに置換
	#print(_feature)
	return np.array(_feature)



class feature_generator:
	""" 特徴ベクトルを作成するクラス
	"""
	def __init__(self, time, data=None):
		time = int(time)
		self._time = time
		self._gen_func = []
		self._data = data
		if data is None:
			self._data = load_weather_library(["47819", "1240", "0962", "47818"])
		if time == 16:
			self._gen_func.append(create_feature16)
		elif time == 18:
			self._gen_func.append(create_feature18)
		elif time == 23:
			self._gen_func.append(create_feature23)
		else:
			print("--target time error--", time)
			exit()

	def get_feature(self, target_date):
		_feature = []
		for func in self._gen_func:
			_feature += list(func(target_date, self._data))
		return np.array(_feature)



def get_vapor_pressure_saturation(Tb):
	""" 水の沸点温度[deg]から、飽和水蒸気圧[hPa]を返す
	気温を空気中の水の温度と仮定しても近い値が得られるようだ。
	Tb 水の沸点[deg]
	"""
	try:
		Tb = float(Tb)
		P_torr = 10 ** (8.07131 - 1730.63 / (233.426 + Tb)) # https://ja.wikipedia.org/wiki/%E8%92%B8%E6%B0%97%E5%9C%A7
		P_hPa = P_torr * 133.322368 / 100.0 # 圧力単位をTorrからhPaへ変換する。https://ja.wikipedia.org/wiki/%E3%83%88%E3%83%AB
		#print(P_hPa)
		return P_hPa
	except:
		pass

def get_Tetens(t):
	""" 気温から飽和水蒸気圧[hPa]を返す
	http://www.s-yamaga.jp/nanimono/taikitoumi/kukichunosuijoki.htm#tetensの式, 同じベージのSonntagの式は間違っているとしか思えん。
	"""
	#T = t + 273.15
	#E_hPa = (math.exp(-6096.9385 * T**-1 + 21.240942 - 2.711193 * 10**-2 + 1.673852 * 10**-5 * T**2 + 2.433502 * math.log(T))) / 100 # Sonntagの式?
	
	a = 7.5
	b = 237.3
	E_hPa = 6.11 * 10 ** (a * t/(b + t))
	#print("飽和水蒸気圧", E_hPa)
	return E_hPa

def get_vapor_pressure(U, t):
	""" 水蒸気圧[hPa]を求める
	U 相対湿度[%]
	t 気温[deg]
	"""
	return U / 100 * get_Tetens(t)


def GofGra(t):
	""" 気温から飽和水蒸気圧[hPa]を求める
	氷点下では別の近似式を使った方が良いらしい。
	http://d.hatena.ne.jp/Rion778/20121126/1353861179
	tの単位：℃
	get_vapor_pressure_xと同じ結果が返ってくるんだが・・・。
	"""
	water_vapor_at_saturation = 10 ** \
	  (10.79574 * (1 - 273.16/(t + 273.15)) - \
	   5.02800 * math.log10((t + 273.15)/273.16) + \
	   1.50475 * 10**(-4) * (1-10**(-8.2969 * ((t + 273.15)/273.16 - 1))) + \
	   0.42873 * 10**(-3) * (10**(4.76955*(1 - 273.16/(t + 273.15))) - 1) + \
	   0.78614)
	return water_vapor_at_saturation


def get_dew_point(U, t):
	""" 露点温度[deg]を返す
	t 気温[deg]
	U 相対湿度[%]
	"""
	dew_point_temperature = -(math.log(GofGra(t)*U/100/6.1078) * 237.3) / \
		(math.log(GofGra(t)*U/100/6.1078) - 17.2693882)
	return dew_point_temperature


def main():
	print(get_vapor_pressure(93, 20.2))
	print(get_vapor_pressure(70, 27.4))
	print(get_vapor_pressure_saturation(20.2))
	print(get_vapor_pressure_saturation(27.4))
	print(GofGra(20.2))
	print(GofGra(27.4))
	print(get_dew_point(94, 22.8))
	print(get_dew_point(70, 27.4))
	#exit()
	weather_library = load_weather_library(["47819", "1240", "0962", "47818"])
	weather_kumamoto = weather_library["47819"]
	print("--wind--")
	for i in range(24):
		hoge = get_measurement_value(dt(2016, 1, 1,  i), weather_kumamoto, "風向")
		print(hoge)
	weather_asootohime = weather_library["1240"]
	print("--temperature--")
	for i in range(24):
		hoge = get_measurement_value(dt(2015, 12, 18,  i), weather_asootohime, "気温")
		print(hoge)
	hoge = create_feature23(dt(2016, 1, 1, 0, 0, 0), weather_library)
	print(hoge)
	hoge = create_feature16(dt(2016, 1, 1, 0, 0, 0), weather_library)
	print(hoge)

if __name__ == '__main__':
	main()
