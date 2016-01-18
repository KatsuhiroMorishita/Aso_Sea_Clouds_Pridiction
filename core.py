#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: core
# purpose: ランダムフォレストを用いて雲海の発生を予測する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import sys
import pandas
import pickle
import math
import time
from sklearn.ensemble import RandomForestRegressor as ml # RandomForestClassifier クラス分けならこれ
from datetime import datetime as dt
from datetime import timedelta as td

import feature
import amedas.download as amd
import amedas.html_parser as amp
import timeKM

# 何日前のデータまで取るか
days = 6
wait_seconds = 0.1                        # たまにプロキシ？ファイヤウォール？が通信をカットするのでその対策.ほとんど意味がなかったが。。



def resolve(txt_bytes):
	""" bytesをstrに変換して、改行コードで区切ったリストを返す
	"""
	txt = txt_bytes.decode(encoding="utf-8-sig", errors="ignore")
	lines = txt.split("\n")
	#print(lines)
	return lines


def get_passed_amedas_data(node_obj, date, term):
	""" dateを起点として、term日分の観測データをダウンロードして返す
	ただし、dateを起点とした過去のデータを返す。
	過去の観測データ用です。
	"""
	lines = []
	# 過去データを入手
	for i in range(1, term):
		print("--wait some seconds--")
		time.sleep(wait_seconds)        # たまにプロキシ？ファイヤウォール？が通信をカットするのでその対策
		_date = date - td(days=i)
		now = dt.now()
		if _date.year == now.year and _date.month == now.month and _date.day == now.day: # 現時点の観測データは対応していない
			continue
		print(_date)
		html_bytes = node_obj.get_data(_type="hourly", date=_date)
		if html_bytes == None:
			print("--can't download--")
			continue
		html_lines = resolve(html_bytes)
		data = amp.get_data(html_lines, _date)
		#print(data)
		lines += [",".join(x) for x in data]
	return lines


def get_amedas_data_typeB(node_obj, date):
	# 過去のデータを取得
	lines = get_passed_amedas_data(node_obj, date, days)
	# 最新のデータを入手
	_date = dt.now() + td(days=1)
	if date.year == _date.year and date.month == _date.month and date.day == _date.day:
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



def get_amedas_data_typeA(node_obj, date):
	# 過去のデータを取得
	lines = get_passed_amedas_data(node_obj, date, days)
	# 最新のデータを入手
	_date = dt.now() + td(days=1)
	if date.year == _date.year and date.month == _date.month and date.day == _date.day:
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
			氷点下では別の近似式を使った方が良いらしい。
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


def get_amedas_data(node_obj, date):
	""" アメダスの観測データを返す
	自動的に判別できればいいのだけど・・・できるかな？
	"""
	if node_obj.name == "阿蘇山":
		return get_amedas_data_typeA(node_obj, date)
	if node_obj.name == "熊本":
		return get_amedas_data_typeA(node_obj, date)
	if node_obj.name == "阿蘇乙姫":
		return get_amedas_data_typeB(node_obj, date)
	


def main():
	# 予想したい日の日付けを設定
	target_date = None
	_day = dt.now()        # まずはコマンドライン引数による指定がない場合を想定
	if _day.hour >= 10:    # この時刻を過ぎると、翌日の予想を実施する
		_day += td(days=1)
	target_date = dt(year=_day.year, month=_day.month, day=_day.day)

	argvs = sys.argv       # コマンドライン引数を格納したリストの取得
	argc = len(argvs)      # 引数の個数
	if argc >= 2:          # 引数で計算対象の日を渡す
		arg = argvs[1]
		arg += " 0:0:0"    # 時分秒を加える
		t = timeKM.getTime(arg)
		if t != None:
			target_date = t	
	print(target_date)

	# 予測を実行する時刻を決定する（引数がなければスクリプト実行時の時刻が使われる）
	process_hour = dt.now().hour
	if argc >= 3:          # 引数で予想実行時刻を渡す（その時刻に雲海が出るかを確認するものではない）
		arg = argvs[2]
		if arg.isdigit():
			process_hour = int(arg)


	# アメダスの観測所オブジェクトを作成
	amedas_nodes = amd.get_amedas_nodes()
	#print(amedas_nodes)
	# 観測データを読み出す
	#node_A = amedas_nodes["阿蘇山"]
	node_A = amedas_nodes["熊本"]        # 2015-09の噴火で阿蘇山頂のデータが得られないので、熊本に差し替え
	lines_A = get_amedas_data(node_A, target_date)
	node_B = amedas_nodes["阿蘇乙姫"]
	lines_B = get_amedas_data(node_B, target_date)
	# 観測データを処理して、特徴量の生成に適したオブジェクトに変更
	weather_data_A = feature.get_weather_dict(lines_A)
	weather_data_B = feature.get_weather_dict(lines_B)
	raw_data = [weather_data_A, weather_data_B]
	#print(weather_data_Aso)
	#print(weather_data_Otohime)


	# 機械学習オブジェクトを生成
	clf = ml()	
	if 23 > process_hour >= 16:
		with open('entry_16.pickle', 'rb') as f:
			clf = pickle.load(f)               # オブジェクト復元
	else:
		with open('entry_23.pickle', 'rb') as f:
			clf = pickle.load(f)               # オブジェクト復元


	# 特徴ベクトルを生成
	_feature = None
	if 23 > process_hour >= 16:
		_feature = feature.create_feature16(target_date, raw_data)
	else:
		_feature = feature.create_feature23(target_date, raw_data)
	print(_feature)

	# 予測を実施
	print("--predict--")
	print("target date: " + str(target_date))
	print("process hur: " + str(process_hour))
	done = False
	results = []
	if _feature != None:
		if not None in _feature:  # Noneがあると計算出来ない
			test = clf.predict(_feature)
			results.append((target_date, test[0], _feature))
			print(test)
			done = True
	if done == False:
		results.append((target_date, "NA", _feature))
		print("--can't predict. There is None data in feature-vector.--")


	# 予測結果を保存
	with open("result.csv", "w") as fw:
		for result in results:
			_date, predict_result, _feature = result
			str_feature = [str(x) for x in _feature]
			fw.write(str(dt.now()))
			fw.write(",")
			fw.write(str(_date))
			fw.write(",")
			fw.write(str(predict_result))
			fw.write(",")
			fw.write("$")
			fw.write(",")
			fw.write(",".join(str_feature))
			fw.write("\n")

	return results


if __name__ == '__main__':
	main()
