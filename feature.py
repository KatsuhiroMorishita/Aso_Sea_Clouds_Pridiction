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
import timeKM


index_B = {"時刻":0, "降水量":1, "気温":2, "風速":3, "風向":4, "日照時間":5}#, "降雪":6, "積雪":7}
index_A = {"時刻":0, "現地気圧":1, "海面気圧":2, "降水量":3, "気温":4, "露点温度":5, "蒸気圧":6, "湿度":7, "風速":8, "風向":9, "日照時間":10, "全天日射量":11, "降雪":12, "積雪":13, "天気":14, "雲量":15, "視程":16}


def get_season(_date):
	""" 日付けをシーズン化したもの
	"""
	return int((_date - datetime.datetime(_date.year, 1, 1)).total_seconds() / (7 * 24 * 3600))



def get_measurement_value(_date, data_set, target_index):
	""" 前日のhour時の観測値
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


def get_diff2(time, data_set1, data_set2, target_index):
	""" 2つのデータセット間の差分を取る
	"""
	v1 = get_measurement_value(time, data_set1, target_index)
	v2 = get_measurement_value(time, data_set2, target_index)
	if v1 is None or v2 is None:
		return None
	else:
		return v1 - v2



def get_values(origin_time, _weather_data, key, term_hours=range(1, 25)):
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


def get_average_wether(_date, _weather_data, key, term_hours=72):
	""" 平均観測値
	集計の仕方が不味いと思うが、まぁ動いているからいいや。
	"""
	weather_data, _index = data_set
	#__date = dt(_date.year, _date.month, _date.day) - td(hours=term_hours)
	__date = _date - td(hours=term_hours)
	values = []
	for i in range(term_hours):
		if __date not in weather_data:
			return None
		one_data = weather_data[__date]
		#print(one_data)
		if one_data == None:
			return None
		values.append(one_data[_index[key]])
		__date += td(hours=1)
	#print(values)
	if not None in values:
		return sum(values) / float(len(values))
	else:
		return None



def get_average_temperature_3days(_date, data_set):
	""" 3日間の平均気温
	集計の仕方が不味いと思うが、まぁ動いているからいいや。
	"""
	weather_data, _index = data_set
	__date = _date - datetime.timedelta(days=3)
	temperature = []
	while __date < _date:
		one_data = weather_data[__date]
		if one_data == None:
			return
		temperature.append(one_data[_index["気温"]])
		__date += datetime.timedelta(hours=1)
	#print(temperature)
	if not None in temperature:
		return sum(temperature) / float(len(temperature))
	else:
		return None


def get_rain_3days(_date, data_set):
	""" 3日間の降水量
	"""
	weather_data, _index = data_set
	__date = _date - datetime.timedelta(days=3)
	rain = []
	while __date < _date:
		one_data = weather_data[__date]
		if one_data == None:
			return
		rain.append(one_data[_index["降水量"]])
		__date += datetime.timedelta(hours=1)
	#print(rain)
	if not None in rain:
		return sum(rain)
	else:
		return None


def get_sunshine_preOneDay(_date, data_set):
	""" 前日の日照時間の累積
	"""
	weather_data, _index = data_set
	__date = _date - datetime.timedelta(days=1)
	sunshine = []
	while __date < _date:
		one_data = weather_data[__date]
		if one_data == None:
			return
		#print(one_data)
		if len(one_data) > _index["日照時間"]: # 欠測対策
			sunshine.append(one_data[_index["日照時間"]])
		else:
			sunshine.append(0.0)
		__date += datetime.timedelta(hours=1)
	#print(sunshine)
	if not None in sunshine:
		return sum(sunshine)
	else:
		return None




def get_average_wind(_date, hour, data_set):
	""" 前日の(hour-2)～hour時における平均風速
	"""
	weather_data, _index = data_set
	_date -= datetime.timedelta(days=1)
	time = _date + datetime.timedelta(hours=hour-2)
	time_end = _date + datetime.timedelta(hours=hour)
	wind = []
	while time <= time_end:
		one_data = weather_data[time]
		if one_data == None:
			return
		wind.append(one_data[_index["風速"]])
		time += datetime.timedelta(hours=1)
	#print(wind)
	if None in wind:
		return None
	else:
		return sum(wind) / float(len(wind))



def get_TTd(_date, hour, data_set):
	""" 前日のhour時における湿数
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



def get_diff_air_pressure(_date, hour, data_set):
	""" 前日のhour時と前々日のhour時における気圧差
	"""
	weather_data, _index = data_set
	_date -= datetime.timedelta(days=2)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data[_date]
	if one_data == None:
		return
	pressure1 = one_data[_index["現地気圧"]]
	_date += datetime.timedelta(hours=24) # 24時間後=前日のhour時
	one_data = weather_data[_date]
	if one_data == None:
		return
	pressure2 = one_data[_index["現地気圧"]]
	if pressure1 == None or pressure2 == None:
		return
	return pressure1 - pressure2


def get_bias_air_pressure(_date, hour, data_set, term_days=6):
	""" 前日のhour時における気圧の平均からのズレ
	"""
	weather_data, _index = data_set
	#print("--debug msg, get_bias_air_pressure_pointA--")
	time = _date - datetime.timedelta(days=term_days)
	time += datetime.timedelta(hours=hour)
	#print(weather_data)
	keys = sorted(weather_data.keys())
	#print(keys)
	#for i in range(100):
	#	key = keys[i]
	#	print(weather_data[key])
	#exit()
	p = []
	while time < _date:
		#print("--")
		if not time in weather_data:
			time += datetime.timedelta(days=1)
			#print("A")
			continue
		#print(time)
		one_data = weather_data[time]
		if one_data == None:
			time += datetime.timedelta(days=1)
			#print("B")
			continue
		pressure = one_data[_index["現地気圧"]]
		if pressure != None:               # 未観測ってことはたまにあるようだが、せっかくの学習データを減らしたくない
			p.append(pressure)
		time += datetime.timedelta(days=1)
	if len(p) < 5:                        # 数はテキトー
		return
	average_p = sum(p) / float(len(p))     # pの中にNoneが入っているとエラー
	return p[-1] - average_p               # 何もなければ、p[-1]は_dateの前日のhour時の観測データが入っている。もしかするとNoneで随分離れた時刻ってこともあるかもしれないが・・・。笑





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
			fuga = mem.replace(".", "")
			fuga = fuga.replace(" )", "")            # 観測上のおかしなデータにくっつく記号
			if len(fuga) > 0:
				if "-" == fuga[0]:
					fuga = fuga[1:]
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
	weather_hugendake = weather_library["47818"]
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
	_feature += [get_diff2(dt(y, m, d, 23), weather_hugendake, weather_shimabara, "気温")]
	_feature += [get_average_temperature_3days(_date, weather_asootohime)]
	_feature += [get_average_temperature_3days(_date, weather_asootohime)]
	_feature += [get_rain_3days(_date, weather_asootohime)]
	_feature += [get_sunshine_preOneDay(_date, weather_asootohime)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_asootohime, "風向")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_hugendake, "風速")]
	_feature += [get_average_wind(_date, 23, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 23), weather_kumamoto, "露点温度")]
	#_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "海面気圧")]
	#_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "海面気圧")]
	#_feature += [get_measurement_value(dt(y, m, d, 23), weather_kumamoto, "海面気圧")]
	_feature += [get_TTd(_date, 14, weather_kumamoto)]
	_feature += [get_TTd(_date, 23, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "蒸気圧")]
	_feature += [get_diff_air_pressure(_date, 23, weather_kumamoto)]
	_feature += [get_bias_air_pressure(_date, 23, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "湿度")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 15), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 21), weather_hugendake, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 12), weather_kumamoto, "雲量")]
	_feature += [get_measurement_value(dt(y, m, d, 21), weather_kumamoto, "雲量")]
	#_feature += get_values(_date, weather_kumamoto, "気温", range(1, 24*10))
	#_feature += get_values(_date, weather_kumamoto, "露点温度", range(1, 24*10))
	#_feature += get_values(_date, weather_kumamoto, "日照時間", range(1, 24*10))
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
	pre_date = _date - td(days=1)
	y, m, d = pre_date.year, pre_date.month, pre_date.day
	_feature = []
	_feature += [get_season(_date)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_asootohime, "気温")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "気温")]
	_feature += [get_measurement_value(dt(y, m, d, 14), weather_kumamoto, "気温")]
	_feature += [get_average_temperature_3days(_date, weather_asootohime)]
	_feature += [get_rain_3days(_date, weather_asootohime)]
	_feature += [get_sunshine_preOneDay(_date, weather_asootohime)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風速")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_asootohime, "風向")]
	_feature += [get_average_wind(_date, 16, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "露点温度")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "海面気圧")]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "海面気圧")]
	_feature += [get_TTd(_date, 16, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "蒸気圧")]
	_feature += [get_diff_air_pressure(_date, 16, weather_kumamoto)]
	_feature += [get_bias_air_pressure(_date, 16, weather_kumamoto)]
	_feature += [get_measurement_value(dt(y, m, d, 16), weather_kumamoto, "湿度")]
	_feature += [get_measurement_value(dt(y, m, d,  6), weather_kumamoto, "視程")]
	_feature += [get_measurement_value(dt(y, m, d, 15), weather_kumamoto, "視程")]
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
		elif time == 23:
			self._gen_func.append(create_feature23)
		else:
			print("--target time error--")
			exit()

	def get_feature(self, target_date):
		_feature = []
		for func in self._gen_func:
			_feature += list(func(target_date, self._data))
		return np.array(_feature)



def main():
	weather_library = load_weather_library(["47819", "1240", "0962", "47818"])
	hoge = create_feature23(dt(2016, 1, 1, 0, 0, 0), weather_library)
	print(hoge)
	hoge = create_feature16(dt(2016, 1, 1, 0, 0, 0), weather_library)
	print(hoge)

if __name__ == '__main__':
	main()
