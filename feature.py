#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: feature
# purpose: 雲海出現を予測するために必要な特徴量を作成する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
#地点A　阿蘇山頂, 地点B　阿蘇乙姫
import datetime
import timeKM


index_B = {"時刻":0, "降水量":1, "気温":2, "風速":3, "風向":4, "日照時間":5}#, "降雪":6, "積雪":7}
index_A = {"時刻":0, "現地気圧":1, "海面気圧":2, "降水量":3, "気温":4, "露点温度":5, "蒸気圧":6, "湿度":7, "風速":8, "風向":9, "日照時間":10, "全天日射量":11, "降雪":12, "積雪":13, "天気":14, "雲量":15, "視程":16}


def get_season(_date, hour, weather_data_A, weather_data_B):
	""" 日付けをシーズン化したもの
	"""
	return int((_date - datetime.datetime(_date.year, 1, 1)).total_seconds() / (7 * 24 * 3600))


def get_temperature_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時の気温　地点B
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_B[_date]
	if one_data == None:
			return
	temperature = one_data[index_B["気温"]]
	return temperature



def get_average_temperature_3days_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 3日間の平均気温　地点B
	集計の仕方が不味いと思うが、まぁ動いているからいいや。
	"""
	__date = _date - datetime.timedelta(days=3)
	temperature = []
	while __date < _date:
		one_data = weather_data_B[__date]
		if one_data == None:
			return
		temperature.append(one_data[index_B["気温"]])
		__date += datetime.timedelta(hours=1)
	#print(temperature)
	if not None in temperature:
		return sum(temperature) / float(len(temperature))
	else:
		return None


def get_rain_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 3日間の降水量　地点B
	"""
	__date = _date - datetime.timedelta(days=3)
	rain = []
	while __date < _date:
		one_data = weather_data_B[__date]
		if one_data == None:
			return
		rain.append(one_data[index_B["降水量"]])
		__date += datetime.timedelta(hours=1)
	#print(rain)
	if not None in rain:
		return sum(rain)
	else:
		return None


def get_sunshine_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の日照時間の累積　地点A
	"""
	__date = _date - datetime.timedelta(days=1)
	sunshine = []
	while __date < _date:
		one_data = weather_data_B[__date]
		if one_data == None:
			return
		#print(one_data)
		if len(one_data) > index_B["日照時間"]: # 欠測対策
			sunshine.append(one_data[index_B["日照時間"]])
		else:
			sunshine.append(0.0)
		__date += datetime.timedelta(hours=1)
	#print(sunshine)
	if not None in sunshine:
		return sum(sunshine)
	else:
		return None


def get_temperature_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における気温　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	temperature = one_data[index_A["気温"]]
	return temperature


def get_temperature23_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の23時における気温　地点B
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=23)
	one_data = weather_data_B[_date]
	if one_data == None:
			return
	temperature = one_data[index_B["気温"]]
	return temperature


def get_temperature_diff_pointAB(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における気温差　地点A-地点B
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	temperature_A = one_data[index_A["気温"]]
	one_data = weather_data_B[_date]
	if one_data == None:
			return
	temperature_B = one_data[index_B["気温"]]
	if temperature_A != None and temperature_B != None:
		return temperature_A - temperature_B
	else:
		return None

def get_temperature_diff18toX_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の18時-hour時における気温差　地点A
	"""
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=18)
	time2 = _date + datetime.timedelta(hours=hour)
	one_data = weather_data_A[time1]
	if one_data == None:
			return
	temperature_1 = one_data[index_A["気温"]]
	one_data = weather_data_A[time2]
	if one_data == None:
			return
	temperature_2 = one_data[index_A["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None

def get_temperature_diff18toX_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 前日の18時-hour時における気温差　地点B
	"""
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=18)
	time2 = _date + datetime.timedelta(hours=hour)
	one_data = weather_data_B[time1]
	if one_data == None:
			return
	temperature_1 = one_data[index_B["気温"]]
	one_data = weather_data_B[time2]
	if one_data == None:
			return
	temperature_2 = one_data[index_B["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None


def get_temperature_diff06to14_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の06時-14時における気温差　地点A
	"""
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=6)
	time2 = _date + datetime.timedelta(hours=14)
	one_data = weather_data_A[time1]
	if one_data == None:
		#print("--fuga--")
		return
	temperature_1 = one_data[index_A["気温"]]
	one_data = weather_data_A[time2]
	if one_data == None:
		#print("--hoge--")
		return
	temperature_2 = one_data[index_A["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None


def get_temperature_diff06to14_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 前日の06時-14時における気温差　地点B
	"""
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=6)
	time2 = _date + datetime.timedelta(hours=14)
	one_data = weather_data_B[time1]
	if one_data == None:
			return
	temperature_1 = one_data[index_B["気温"]]
	one_data = weather_data_B[time2]
	if one_data == None:
			return
	temperature_2 = one_data[index_B["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None


def get_wind_pointB(_date, hour, weather_data_A, weather_data_B):
	""" 前日の23時における風速　地点B
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_B[_date]
	if one_data == None:
			return
	wind = one_data[index_B["風速"]]
	return wind

def get_wind_direction_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における風向　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	direction = one_data[index_A["風向"]]
	#print(direction)
	if direction != None and direction != 0.0:
		label = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東", "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西", "静穏"]
		return label.index(direction)#int(label.index(direction) / 4)
	else:
		return None

def get_wind_night_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の(hour-2)-hour時における風速　地点A
	"""
	_date -= datetime.timedelta(days=1)
	time = _date + datetime.timedelta(hours=hour-2)
	time_end = _date + datetime.timedelta(hours=hour)
	wind = []
	while time <= time_end:
		one_data = weather_data_A[time]
		if one_data == None:
			return
		wind.append(one_data[index_A["風速"]])
		time += datetime.timedelta(hours=1)
	#print(wind)
	if None in wind:
		return None
	else:
		return sum(wind) / float(len(wind))


def get_dew_temperature_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における露点温度　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	temperature = one_data[index_A["露点温度"]]
	return temperature

def get_TTd_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における湿数　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	T = one_data[index_A["気温"]]
	Td = one_data[index_A["露点温度"]]
	TTd = None
	if T != None and Td != None:
		TTd = T - Td
	return TTd


def get_vapor_pressure_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における蒸気圧　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	vapor_pressure = one_data[index_A["蒸気圧"]]
	return vapor_pressure


def get_diff_air_pressure_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時と前々日のhour時における気圧差　地点A
	"""
	_date -= datetime.timedelta(days=2)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
		return
	pressure1 = one_data[index_A["現地気圧"]]
	_date += datetime.timedelta(hours=24) # 24時間後=前日のhour時
	one_data = weather_data_A[_date]
	if one_data == None:
		return
	pressure2 = one_data[index_A["現地気圧"]]
	if pressure1 == None or pressure2 == None:
		return
	return pressure1 - pressure2


def get_bias_air_pressure_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における気圧の平均からのズレ　地点A
	"""
	#print("--debug msg, get_bias_air_pressure_pointA--")
	time = _date - datetime.timedelta(days=30)
	time += datetime.timedelta(hours=hour)
	#print(weather_data_A)
	keys = sorted(weather_data_A.keys())
	#print(keys)
	#for i in range(100):
	#	key = keys[i]
	#	print(weather_data_A[key])
	#exit()
	p = []
	while time < _date:
		#print("--")
		if not time in weather_data_A:
			time += datetime.timedelta(days=1)
			#print("A")
			continue
		#print(time)
		one_data = weather_data_A[time]
		if one_data == None:
			time += datetime.timedelta(days=1)
			#print("B")
			continue
		pressure = one_data[index_A["現地気圧"]]
		if pressure != None:               # 未観測ってことはたまにあるようだが、せっかくの学習データを減らしたくない
			p.append(pressure)
		time += datetime.timedelta(days=1)
	if len(p) < 5:                        # 数はテキトー
		return
	average_p = sum(p) / float(len(p))     # pの中にNoneが入っているとエラー
	return p[-1] - average_p               # 何もなければ、p[-1]は_dateの前日のhour時の観測データが入っている。もしかするとNoneで随分離れた時刻ってこともあるかもしれないが・・・。笑



def get_humidity_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日のhour時における湿度　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	humidity = one_data[index_A["気温"]]
	return humidity
	pass


def get_sight_range23_pointA(_date, hour, weather_data_A, weather_data_B):
	""" 前日の23時における視程　地点A
	"""
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=23)
	one_data = weather_data_A[_date]
	#print(one_data)
	if one_data == None:
			return
	sight_range = one_data[index_A["視程"]]
	return sight_range
	pass




def get_weather_dict(lines, th):
	""" 気象データの辞書を返す
	"""
	weather_dict = {}
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
			fuga = fuga.replace(" )", "")          # 観測上のおかしなデータにくっつく記号
			if len(fuga) > 0:
				if "-" == fuga[0]:
					fuga = fuga[1:]
			fuga = fuga.replace("-", "")           # -10, 10-　みたいなパターン。数値の前のマイナス符号があれば負値。
			if fuga.isdigit() == True:
				mem = mem.replace(" )", "")
				if "-" == mem[-1]:                 # 10-　みたいなパターンへの対応
					mem = mem[:-1]
				new_field.append(float(mem))
			else:
				if mem == "":
					new_field.append(0.0)
				elif mem == "×" or mem == "///":   # 恐らく、非観測項目にくっつく記号
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


def read_weather_data(fpath, th):
	"""
	気象データを読み込む
	"""
	weather_dict = {}
	with open(fpath, "r", encoding="utf-8-sig") as fr:
		lines = fr.readlines()
		weather_dict = get_weather_dict(lines, th)
	return weather_dict


def create_feature23(_date, weather_data_A, weather_data_B):
	""" 特徴ベクトルを作る
	"""
	print("feature of ", _date)
	_feature = [
		get_season(_date, None, weather_data_A, weather_data_B), \
		get_temperature_pointB(_date, 14, weather_data_A, weather_data_B), \
		get_temperature_pointB(_date, 6, weather_data_A, weather_data_B), \
		get_average_temperature_3days_pointB(_date, None, weather_data_A, weather_data_B), \
		get_rain_pointB(_date, None, weather_data_A, weather_data_B), \
		get_sunshine_pointA(_date, None, weather_data_A, weather_data_B), \
		get_temperature_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_temperature_diff_pointAB(_date, 23, weather_data_A, weather_data_B), \
		get_temperature_diff18toX_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_temperature_diff18toX_pointB(_date, 23, weather_data_A, weather_data_B), \
		get_temperature_diff06to14_pointA(_date, None, weather_data_A, weather_data_B), \
		get_temperature_diff06to14_pointB(_date, None, weather_data_A, weather_data_B), \
		get_wind_pointB(_date, 23, weather_data_A, weather_data_B), \
		get_wind_direction_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_wind_night_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_dew_temperature_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_TTd_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_vapor_pressure_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_diff_air_pressure_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_bias_air_pressure_pointA(_date, 23, weather_data_A, weather_data_B), \
		get_humidity_pointA(_date, 23, weather_data_A, weather_data_B) \
		#get_sight_range23_pointA(_date, weather_data_A, weather_data_B) \ # 視程は311移行に活発になった噴火で観測されなくなっている
		]
	#print("fuga")
	return _feature



def create_feature16(_date, weather_data_A, weather_data_B):
	""" 特徴ベクトルを作る
	"""
	print("feature of ", _date)
	_feature = [
		get_season(_date, None, weather_data_A, weather_data_B), \
		get_temperature_pointB(_date, 14, weather_data_A, weather_data_B), \
		get_temperature_pointB(_date, 6, weather_data_A, weather_data_B), \
		get_average_temperature_3days_pointB(_date, None, weather_data_A, weather_data_B), \
		get_rain_pointB(_date, None, weather_data_A, weather_data_B), \
		get_sunshine_pointA(_date, None, weather_data_A, weather_data_B), \
		get_temperature_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_temperature_diff_pointAB(_date, 16, weather_data_A, weather_data_B), \
		get_temperature_diff06to14_pointA(_date, None, weather_data_A, weather_data_B), \
		get_temperature_diff06to14_pointB(_date, None, weather_data_A, weather_data_B), \
		get_wind_pointB(_date, 16, weather_data_A, weather_data_B), \
		get_wind_direction_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_wind_night_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_dew_temperature_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_TTd_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_vapor_pressure_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_diff_air_pressure_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_bias_air_pressure_pointA(_date, 16, weather_data_A, weather_data_B), \
		get_humidity_pointA(_date, 16, weather_data_A, weather_data_B) \
		#get_sight_range23_pointA(_date, weather_data_A, weather_data_B) \ # 視程は311移行に活発になった噴火で観測されなくなっている
		]
	#print("fuga")
	return _feature

