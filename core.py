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
import os
import numpy as np
import pandas
import pickle
import math
import time
import machine as mc
from datetime import datetime as dt
from datetime import timedelta as td

import feature
import amedas.download as amd
import amedas.html_parser as amp
import timeKM

# 何日前のデータまで取るか
days = 6
wait_seconds = 0.1                        # たまにプロキシ？ファイヤウォール？が通信をカットするのでその対策.ほとんど意味がなかったが。。



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
		html_txt = node_obj.get_data(_type="hourly", date=_date)
		if html_txt is None:
			print("--can't download--")
			continue
		html_lines = html_txt.split("\n")
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
		html_txt = node_obj.get_data(_type="real-time")
		html_lines = html_txt.split("\n")
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
		html_txt = node_obj.get_data(_type="real-time")
		html_lines = html_txt.split("\n")
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
	含まれる情報別に、ダウンロード後の文字列解析に使う関数を使い分けている。
	"""
	if int(node_obj.block_no) > 47000:
		return get_amedas_data_typeA(node_obj, date)
	else:
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

	# 予報する対象の時刻
	target_time = 23
	if 23 > process_hour >= 16:
		target_time = 16


	# アメダスの観測所オブジェクトを作成
	amedas_nodes = amd.get_amedas_nodes()
	#print(amedas_nodes)
	# 特徴ベクトルを生成するオブジェクトの用意
	features_dict = {}
	for block_no in ["47819", "1240", "0962", "47818"]:
		node = amedas_nodes[block_no]
		lines = get_amedas_data(node, target_date)
		weather_data = feature.get_weather_dict(lines)
		if int(node.block_no) > 47000:
			features_dict[block_no] = [weather_data, feature.index_A]
		else:
			features_dict[block_no] = [weather_data, feature.index_B]
	fg_obj = feature.feature_generator(target_time, features_dict)
	#print(weather_data_Aso)
	#print(weather_data_Otohime)

	# 機械学習オブジェクトを生成
	clf = mc.load(os.path.abspath("./learned_machine/time" + str(target_time)))
	print(type(clf))

	# 特徴ベクトルを生成
	_feature = fg_obj.get_feature(target_date)
	_feature = np.array([_feature]) # TensorFlowはnumpy.arrayの2重の入れ子でないと動かない
	print(_feature)

	# 予測を実施
	print("--predict--")
	print("target date: " + str(target_date))
	print("process hur: " + str(process_hour))

	results = []
	#if _feature != None:
	#if not None in _feature:  # Noneがあると計算出来ない
	test = clf.predict(_feature)
	results.append((target_date, test[0], _feature))
	print(test)


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
