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
import timeKM


index_B = {"時刻":0, "降水量":1, "気温":2, "風速":3, "風向":4, "日照時間":5}#, "降雪":6, "積雪":7}
index_A = {"時刻":0, "現地気圧":1, "海面気圧":2, "降水量":3, "気温":4, "露点温度":5, "蒸気圧":6, "湿度":7, "風速":8, "風向":9, "日照時間":10, "全天日射量":11, "降雪":12, "積雪":13, "天気":14, "雲量":15, "視程":16}


def get_season(_date):
	""" 日付けをシーズン化したもの
	"""
	return int((_date - datetime.datetime(_date.year, 1, 1)).total_seconds() / (7 * 24 * 3600))



def get_measurement_value(_date, hour, raw_data, target_index):
	""" 前日のhour時の観測値
	"""
	weather_data, _index = raw_data
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
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



def get_average_temperature_3days(_date, raw_data):
	""" 3日間の平均気温
	集計の仕方が不味いと思うが、まぁ動いているからいいや。
	"""
	weather_data, _index = raw_data
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


def get_rain_3days(_date, raw_data):
	""" 3日間の降水量
	"""
	weather_data, _index = raw_data
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


def get_sunshine_preOneDay(_date, raw_data):
	""" 前日の日照時間の累積
	"""
	weather_data, _index = raw_data
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



def get_temperature_diff_pointAB(_date, hour, raw_data):
	""" 前日のhour時における気温差　地点A-地点B
	"""
	data_A, data_B = raw_data
	weather_data_A, _index_A = data_A
	weather_data_B, _index_B = data_B
	_date -= datetime.timedelta(days=1)
	_date += datetime.timedelta(hours=hour)
	one_data = weather_data_A[_date]
	if one_data == None:
			return
	temperature_A = one_data[_index_A["気温"]]
	one_data = weather_data_B[_date]
	if one_data == None:
			return
	temperature_B = one_data[_index_B["気温"]]
	if temperature_A != None and temperature_B != None:
		return temperature_A - temperature_B
	else:
		return None

def get_temperature_diff18toX(_date, hour, raw_data):
	""" 前日の18時-hour時における気温差
	"""
	weather_data, _index = raw_data
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=18)
	time2 = _date + datetime.timedelta(hours=hour)
	one_data = weather_data[time1]
	if one_data == None:
			return
	temperature_1 = one_data[_index["気温"]]
	one_data = weather_data[time2]
	if one_data == None:
			return
	temperature_2 = one_data[_index["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None


def get_temperature_diff06to14(_date, raw_data):
	""" 前日の06時-14時における気温差
	"""
	weather_data, _index = raw_data
	_date -= datetime.timedelta(days=1)
	time1 = _date + datetime.timedelta(hours=6)
	time2 = _date + datetime.timedelta(hours=14)
	one_data = weather_data[time1]
	if one_data == None:
		#print("--fuga--")
		return
	temperature_1 = one_data[_index["気温"]]
	one_data = weather_data[time2]
	if one_data == None:
		#print("--hoge--")
		return
	temperature_2 = one_data[_index["気温"]]
	if temperature_1 != None and temperature_2 != None:
		return temperature_1 - temperature_2
	else:
		return None



def get_average_wind(_date, hour, raw_data):
	""" 前日の(hour-2)～hour時における平均風速
	"""
	weather_data, _index = raw_data
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



def get_TTd(_date, hour, raw_data):
	""" 前日のhour時における湿数
	"""
	weather_data, _index = raw_data
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



def get_diff_air_pressure(_date, hour, raw_data):
	""" 前日のhour時と前々日のhour時における気圧差
	"""
	weather_data, _index = raw_data
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


def get_bias_air_pressure(_date, hour, raw_data):
	""" 前日のhour時における気圧の平均からのズレ
	"""
	weather_data, _index = raw_data
	#print("--debug msg, get_bias_air_pressure_pointA--")
	time = _date - datetime.timedelta(days=30)
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


def read_weather_data(fpath):
	""" 気象データをファイルから読み込む
	"""
	weather_dict = {}
	with open(fpath, "r", encoding="utf-8-sig") as fr:
		lines = fr.readlines()
		if len(lines) == 0:
			return {}
		#print(str(lines[0:100]))
		weather_dict = get_weather_dict(lines)
	return weather_dict


def read_raw_data(fnames=["amedas_kumamoto.csv", "amedas_asoOtohime.csv"]):
	""" ファイルから観測データを読みだす
	"""
	ans = []
	for fname in fnames:
		weather_data = read_weather_data(fname)
		#print(len(weather_data))
		ans.append(weather_data)
	return ans


def create_feature23(_date, raw_data):
	""" 23時時点での予想を実施する特徴ベクトルを作る
	"""
	print("feature of ", _date)
	weather_data_A, weather_data_B = raw_data
	#print(str(weather_data_A[_date]))
	_feature = [
		get_season(_date), \
		get_measurement_value(_date, 14, [weather_data_B, index_B], "気温"), \
		get_measurement_value(_date, 6, [weather_data_B, index_B], "気温"), \
		get_average_temperature_3days(_date, [weather_data_B, index_B]), \
		get_rain_3days(_date, [weather_data_B, index_B]), \
		get_sunshine_preOneDay(_date, [weather_data_B, index_B]), \
		get_measurement_value(_date, 23, [weather_data_B, index_B], "気温"), \
		get_temperature_diff_pointAB(_date, 23, [[weather_data_A, index_A], [weather_data_B, index_B]]), \
		get_temperature_diff18toX(_date, 23, [weather_data_A, index_A]), \
		get_temperature_diff18toX(_date, 23, [weather_data_B, index_B]), \
		get_temperature_diff06to14(_date, [weather_data_A, index_A]), \
		get_temperature_diff06to14(_date, [weather_data_B, index_B]), \
		get_measurement_value(_date, 23, [weather_data_B, index_B], "風速"), \
		get_measurement_value(_date, 23, [weather_data_A, index_A], "風向"), \
		get_average_wind(_date, 23, [weather_data_A, index_A]), \
		get_measurement_value(_date, 23, [weather_data_A, index_A], "露点温度"), \
		get_TTd(_date, 23, [weather_data_A, index_A]), \
		get_measurement_value(_date, 23, [weather_data_A, index_A], "蒸気圧"), \
		get_diff_air_pressure(_date, 23, [weather_data_A, index_A]), \
		get_bias_air_pressure(_date, 23, [weather_data_A, index_A]), \
		get_measurement_value(_date, 23, [weather_data_A, index_A], "湿度"), \
		# 視程は311移行に活発になった噴火で観測されなくなっている
		]
	#print("fuga")
	_feature = [-99999 if x == None else x for x in _feature] # 欠損値を-99999に置換
	return _feature



def create_feature16(_date, raw_data):
	""" 16時時点での予想を実施する特徴ベクトルを作る
	"""
	print("feature of ", _date)
	weather_data_A, weather_data_B = raw_data
	_feature = [
		get_season(_date), \
		get_measurement_value(_date, 14, [weather_data_B, index_B], "気温"), \
		get_measurement_value(_date, 6, [weather_data_B, index_B], "気温"), \
		get_average_temperature_3days(_date, [weather_data_B, index_B]), \
		get_rain_3days(_date, [weather_data_B, index_B]), \
		get_sunshine_preOneDay(_date, [weather_data_B, index_B]), \
		get_measurement_value(_date, 16, [weather_data_B, index_B], "気温"), \
		get_temperature_diff_pointAB(_date, 16, [[weather_data_A, index_A], [weather_data_B, index_B]]), \
		get_temperature_diff06to14(_date, [weather_data_A, index_A]), \
		get_temperature_diff06to14(_date, [weather_data_B, index_B]), \
		get_measurement_value(_date, 16, [weather_data_B, index_B], "風速"), \
		get_measurement_value(_date, 16, [weather_data_A, index_A], "風向"), \
		get_average_wind(_date, 16, [weather_data_A, index_A]), \
		get_measurement_value(_date, 16, [weather_data_A, index_A], "露点温度"), \
		get_TTd(_date, 16, [weather_data_A, index_A]), \
		get_measurement_value(_date, 16, [weather_data_A, index_A], "蒸気圧"), \
		get_diff_air_pressure(_date, 16, [weather_data_A, index_A]), \
		get_bias_air_pressure(_date, 16, [weather_data_A, index_A]), \
		get_measurement_value(_date, 16, [weather_data_A, index_A], "湿度"), \
		# 視程は311移行に活発になった噴火で観測されなくなっている
		]
	#print("fuga")
	_feature = [-99999 if x == None else x for x in _feature] # 欠損値を-99999に置換
	return _feature

