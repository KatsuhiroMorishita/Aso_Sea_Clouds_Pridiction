#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: predict
# purpose: ランダムフォレストを用いた、雲海出現を予測する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import pandas
import pickle
import math
from sklearn.ensemble import RandomForestRegressor as ml # RandomForestClassifier クラス分けならこれ
from datetime import datetime as dt
from datetime import timedelta as td
import feature
import amedas.download as amd
import amedas.html_parser as amp

# 何日前のデータまで取るか
days = 5



def resolve(txt_bytes):
	""" bytesをstrに変換して、改行コードで区切ったリストを返す
	"""
	txt = txt_bytes.decode(encoding="utf-8-sig", errors="ignore")
	lines = txt.split("\n")
	#print(lines)
	return lines



def get_amedas_data_typeA(node_obj):
	lines = []
	# 過去データを入手
	for i in range(1,days):
		_date = dt.now()-td(days=i)
		print(_date)
		html_bytes = node_obj.get_data(_type="hourly", date=_date)
		html_lines = resolve(html_bytes)
		data = amp.get_data(html_lines, _date)
		#print(data)
		lines += [",".join(x) for x in data]
	# 最新のデータを入手
	html_bytes = node_obj.get_data(_type="real-time")
	html_lines = resolve(html_bytes)
	data = amp.get_data(html_lines, dt.now())
	print(data)
	# 最新の観測データは過去の観測データとフォーマットが異なるので、整形する
	# 降水量と気温を入れ替える
	dummy = []
	for mem in data:
		x = mem.pop(3)
		mem.insert(2, x)
		dummy.append(mem)
	data = dummy
	"""
	for i in range(len(data)):
		x = data[i][1]
		y = data[i][2]
		data[i][1] = y
		data[i][2] = x
	"""
	# 風速と風向を入れ替える
	dummy = []
	for mem in data:
		x = mem.pop(5)
		mem.insert(4, x)
		dummy.append(mem)
	data = dummy
	# 無い観測データ項目を追加
	data = [y + ["", ""] for y in data]
	#print(data)

	# join時にエラーが出ないように全てを文字列化
	dummy = []
	for x in data:
		x = [str(y) for y in x]
		dummy.append(x)
	data = dummy
	#print(data)
	lines += [",".join(x) for x in data]
	#print(lines)
	return lines



def get_amedas_data_typeB(node_obj):
	lines = []
	# 過去のデータを入手
	for i in range(1,days):
		_date = dt.now()-td(days=i)
		print(_date)
		html_bytes = node_obj.get_data(_type="hourly", date=_date)
		html_lines = resolve(html_bytes)
		data = amp.get_data(html_lines, _date)
		#print(data)
		lines += [",".join(x) for x in data]
	# 最新のデータを入手
	html_bytes = node_obj.get_data(_type="real-time")
	html_lines = resolve(html_bytes)
	data = amp.get_data(html_lines, dt.now())
	print(data)
	# 最新の観測データは過去の観測データとフォーマットが異なるので、整形する
	# 気圧を入れ替える
	dummy = []
	for mem in data:
		x = mem.pop(8)
		mem.insert(2, x)
		mem.insert(3, "")
		dummy.append(mem)
	data = dummy
	# 降水量と気温を入れ替える
	dummy = []
	for mem in data:
		x = mem.pop(5)
		mem.insert(4, x)
		dummy.append(mem)
	data = dummy
	# 露点温度、蒸気圧の欄を作る
	dummy = []
	for mem in data:
		mem.insert(6, "")
		mem.insert(6, "")
		dummy.append(mem)
	data = dummy
	# 湿度の位置を変える
	dummy = []
	for mem in data:
		x = mem.pop(11)
		mem.insert(8, x)
		dummy.append(mem)
	data = dummy
	"""
	for i in range(len(data)):
		x = data[i][1]
		y = data[i][2]
		data[i][1] = y
		data[i][2] = x
	"""
	# 風速と風向を入れ替える
	dummy = []
	for mem in data:
		x = mem.pop(10)
		mem.insert(9, x)
		dummy.append(mem)
	data = dummy
	# 無い観測データ項目を追加
	data = [y + ["", "", "", "", "", ""] for y in data]

	# 水蒸気圧を計算する
	dummy = []
	for mem in data:
		P_hPa = ""
		try:
			Tb = float(mem[5])
			#print("hoge")
			#print(Tb)
			P_torr = 10 ** (8.07131 - 1730.63 / (233.426 + Tb)) # https://ja.wikipedia.org/wiki/%E8%92%B8%E6%B0%97%E5%9C%A7
			P_hPa = P_torr * 133.322368 / 100.0 # https://ja.wikipedia.org/wiki/%E3%83%88%E3%83%AB
			#print(P_hPa)
		except:
			pass
		mem[7] = P_hPa
		dummy.append(mem)
	data = dummy

	# 露点温度を計算する
	def GofGra(t):
		""" 気温から飽和水蒸気量を求める
		氷点下では別の近似式を使ったほうがいいらしい。
		http://d.hatena.ne.jp/Rion778/20121126/1353861179
		tの単位：℃
		"""
		water_vapor_at_saturation = 10 ** \
		  (10.79574 * (1 - 273.16/(t + 273.15)) - \
		   5.02800 * math.log10((t + 273.15)/273.16) + \
		   1.50475 * 10**(-4) * (1-10**(-8.2969 * ((t + 273.15)/273.16 - 1))) + \
		   0.42873 * 10**(-3) * (10**(4.76955*(1 - 273.16/(t + 273.15))) - 1) + \
		   0.78614)
		return water_vapor_at_saturation

	dummy = []
	for mem in data: # http://d.hatena.ne.jp/Rion778/20121208/1354975888
		dew_point_temperature = ""
		try:
			t = float(mem[5]) # 気温[deg]
			U = float(mem[8]) # 相対湿度[%]
			#print("@@@")
			#print(t, U)
			dew_point_temperature = -(math.log(GofGra(t)*U/100/6.1078) * 237.3) / \
				(math.log(GofGra(t)*U/100/6.1078) - 17.2693882)
			#print("fuga")
			#print(U)
			#print(dew_point_temperature)
		except:
			pass
		mem[6] = dew_point_temperature
		dummy.append(mem)
	data = dummy
	#print(data)

	# join時にエラーが出ないように全てを文字列化
	dummy = []
	for x in data:
		x = [str(y) for y in x]
		dummy.append(x)
	data = dummy
	#print(data)
	lines += [",".join(x) for x in data]
	return lines


def get_amedas_data(node_obj):
	""" アメダスの観測データを返す
	"""
	if node_obj.name == "阿蘇山":
		return get_amedas_data_typeB(node_obj)
	if node_obj.name == "阿蘇乙姫":
		return get_amedas_data_typeA(node_obj)



def main():
	# 機械学習オブジェクトを生成
	clf = ml()

	# 学習成果を読み出す
	with open('entry.pickle', 'rb') as f:
		clf = pickle.load(f)               # オブジェクト復元

	# アメダスの観測所オブジェクトを作成
	amedas_nodes = amd.get_amedas_nodes()
	#print(amedas_nodes)
	# 観測データを読み出す
	aso_node = amedas_nodes["阿蘇山"]
	aso_lines = get_amedas_data(aso_node)
	otohime_node = amedas_nodes["阿蘇乙姫"]
	otohime_lines = get_amedas_data(otohime_node)
	# 観測データを処理して、特徴量の生成に適したオブジェクトに変更
	weather_data_Aso = feature.get_weather_dict(aso_lines, len(feature.index_A))
	weather_data_Otohime = feature.get_weather_dict(otohime_lines, len(feature.index_B))
	#print(weather_data_Aso)
	#print(weather_data_Otohime)


	# 予想結果をストア
	print("--predict--")
	_day = dt.now()               # 23時以降に実行することを前提に、予想したい日の日付けを設定
	if _day.hour >= 10:
		_day += td(days=1)
	_date = dt(year=_day.year, month=_day.month, day=_day.day)
	print(_date)
	_feature = feature.create_feature(_date, weather_data_Aso, weather_data_Otohime)
	print(_feature)
	done = False
	results = []
	if _feature != None:
		if not None in _feature:  # ランダムフォレスト自体は欠損に強いはずだが、欠損があるとエラーが出たので対策
			test = clf.predict(_feature)
			results.append((_date, test[0]))
			print(test)
			done = True
	if done == False:
		results.append((_date, "NA"))
		print("--can't predict. There is None data in feature-vector.--")


	# 予測結果を保存
	with open("result.csv", "w") as fw:
		for result in results:
			_date, predict_result = result
			fw.write(str(dt.now()))
			fw.write(",")
			fw.write(str(_date))
			fw.write(",")
			fw.write(str(predict_result))
			fw.write("\n")

main()
