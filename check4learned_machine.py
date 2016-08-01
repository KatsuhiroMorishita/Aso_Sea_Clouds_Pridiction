#!usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------
# unkai_data.csvに記載された日付の一部または全部について検証を行い、レポートを作成する
# author: Katsuhiro Morishita
# created: 2016-01-17
# license: MIT
#-------------------------------------------
from datetime import datetime as dt
import os
import sys
import glob
import machine as mc
import numpy

import predict
import feature
import timeKM


def check_date(terms, date):
	""" 日付が期間内にあるかを確認する
	"""
	for date_start, date_end in terms:
		if date_start <= date <= date_end:
			return True
	return False


def read_correct_and_create_features(feature_generator, terms, fname="unkai_date.csv"):
	""" 正解データを読み込んで、特徴ベクトルと共に返す
	raw_data: 気象データ
	"""
	# 観測結果を読み込む
	data = {}
	with open(fname, "r", encoding="utf-8-sig") as fr:
		lines = fr.readlines()
		for line in lines:
			line = line.rstrip()
			date, value, verify_flag = line.split("\t")
			if value == "x":
				#continue
				value = 0# あまりに欠損が多いので、Twitterを信じるなら出なかったものとして扱ってOKだと思う.
			date = timeKM.getTime(date + " 0:0:0")
			if check_date(terms, date):
				data[date] = [value, verify_flag]

	# 教師データを作る
	dates = sorted(data.keys())
	for _date in dates:
		#print(_date)
		_feature = feature_generator.get_feature(_date) # 特徴ベクトルを作る
		#print(_feature)
		if not _feature is None:
			data[_date].append(_feature)

	return data


def sub_process(tag_name, target_dir, feature_generator, terms):
	""" 保存されている学習器を次々と読みだして評価結果をファイルに保存する
	"""
	flist = mc.get_path_list(target_dir) # 学習器のファイルリストを取得
	print(flist)
	if len(flist) == 0:
		print("0 files or dir found.")
		return

	# 正解データと特徴ベクトルを取得
	data = read_correct_and_create_features(feature_generator, terms)

	# 評価用に特徴ベクトルを辞書に格納しなおす
	dates = sorted(data.keys())
	features_dict = {}                                      # 日付をキーとした特徴ベクトル
	for _date in dates:
		features_dict[_date] = (None, data[_date][2], None) # 特徴ベクトルが欲しいだけなので前後をダミーデータを入れている

	# 予想結果を格納する
	predicted_result_dict = {}
	for fpath in flist:
		# 学習器を読みだして復元
		clf = mc.load(fpath)    # オブジェクト復元
		predicted_result = predict.predict2(clf, dates, features_dict)
		predicted_result_dict[fpath] = predicted_result

	# 結果をファイルに保存
	report_path = target_dir + "/learned_machine_report.csv"
	with open(report_path, "w") as fw:
		# 閾値を変えつつ集計
		for th in numpy.arange(0.4, 0.9, 0.2): # th: 閾値
			result = {}                        # 閾値で2値化した結果を格納する
			correct = []
			for fpath in flist:
				predicted_result = predicted_result_dict[fpath]
				if fpath not in result:
					result[fpath] = []
				correct = []
				for _date in dates:
					if _date in predicted_result:
						c = data[_date][0]
						correct.append(c)
						val = float(c) - int((1.0 - th) + predicted_result[_date])
						result[fpath].append(val)

			# 日付を書き込む
			dates_arr = [str(x) for x in dates]
			_str = ",".join(dates_arr)
			fw.write(",date,")
			fw.write(_str)
			fw.write("\n")
			# 正解を書き込む
			correct = [str(c) for c in correct]
			_str = ",".join(correct)
			fw.write(",correct,")
			fw.write(_str)
			fw.write("\n")
			# 結果を書き込む
			for fpath in flist:
				th_data = result[fpath]
				th_data = [str(x) for x in th_data]
				_str = ",".join(th_data)
				fw.write(fpath)          # Excelで閲覧した時に分離させる
				fw.write(",")
				fw.write(str(th))
				fw.write(",")
				fw.write(_str)
				fw.write("\n")
	return report_path


def main_process(target_time, target_dir):
	""" 
	外部からの呼び出しを意識している。
	"""
	# 処理対象の制限（処理時間の短縮になるかも）
	#terms = [(dt(2016, 5, 1), dt(2016, 5, 19))] # for aso
	terms = [(dt(2016, 7, 1), dt(2016, 8, 1))] # for chichibu

	# 引数に合わせて使う特徴ベクトル生成関数を変えて、検証する
	fg_obj = feature.feature_generator(target_time)
	_path = sub_process(target_time, target_dir, fg_obj, terms)

	return [_path]




def main():
	# 引数の処理
	target_time = ""   # 処理対象の時刻を引数で指定
	target_dir = ""
	argvs = sys.argv   # コマンドライン引数を格納したリストの取得
	print(argvs)
	argc = len(argvs)  # 引数の個数
	if argc > 2:
		target_time = argvs[1]
		target_dir = argvs[2]
	else:
		print("input target-number and target-dir.")
		exit()

	if not os.path.exists(target_dir):
		print("no such directry: ", target_dir)
		exit()
	main_process(target_time, target_dir)


if __name__ == '__main__':
	main()
