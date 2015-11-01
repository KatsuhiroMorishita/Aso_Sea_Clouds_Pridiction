#!usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------
# 自動的に学習と検証を行い、レポートを作成する
# 特徴量の検証ではない
# author: Katsuhiro Morishita
# created: 2015-10-25
# license: MIT
#-------------------------------------------
from datetime import datetime as dt
import sys

import learning
import predict
import feature
import create_learning_data
import timeKM

feature_func = feature.create_feature23
try_times = 1500

def main():
	# 引数の処理
	tag_name = ""     # 保存するファイル名にタグを付けることができる
	argvs = sys.argv  # コマンドライン引数を格納したリストの取得
	print(argvs)
	argc = len(argvs) # 引数の個数
	if argc > 1:
		tag_name = "_" + argvs[1]

	# アメダスの観測データを読みだす
	raw_data = feature.read_raw_data()

	# 検証用の正解データを取得する
	correct_result = {}
	with open("correct_result.csv", "r") as fr:
		lines = fr.readlines()
		for line in lines:
			line = line.rstrip()
			date, value = line.split(",")
			date = timeKM.getTime(date + " 0:0:0")
			if value.isdigit():
				value = float(value)
			correct_result[date] = value

	# 教師データ作成の準備
	terms = [(dt(2005, 3, 10), dt(2013, 8, 1)), (dt(2015, 6, 23), dt(2015, 8, 24))]
	tc = create_learning_data.teacher_creator(raw_data, feature_func, terms) # 一度メモリ内に教師データを作成するが、時間がかかる。

	# 学習とその検証を繰り返して、結果をファイルに保存する
	with open("verify_report" + tag_name + ".csv", "w") as fw:
		dates = sorted(correct_result.keys())
		start_date = dates[0]
		end_date = dates[-1]
		for i in range(try_times):
			print("--try count: {0}/{1}--".format(i, try_times))
			# 教師データを作成
			fname = tc.save_teacher()
			training_data = learning.read_training_data(fname)
			# 学習
			clf = learning.learn(training_data, 'entry_temp{0}_{1:05d}.pickle'.format(tag_name, i))
			result = predict.predict(clf, start_date, end_date, feature_func, raw_data)    # 渡す特徴ベクトル生成関数は状況に合わせる
			# 結果の集計
			scale = 10
			zero = [0.0] * scale
			one = [0.0] * scale
			for date in dates:
				if date in result:
					try:
						c = correct_result[date]
						val = c - result[date]
						if int(c) == 0:
							zero[abs(int(val * scale))] += 1
						elif int(c) == 1:
							one[abs(int(val * scale))] += 1
						#print(val)
					except:
						pass
			# ファイルへの保存
			zero = [str(x / sum(zero)) for x in zero] # 正規化
			one = [str(x / sum(one)) for x in one]
			fw.write("{0},".format(i))
			fw.write(",".join(zero))
			fw.write(",,") # Excelで閲覧した時に分離させる
			fw.write(",".join(one))
			fw.write("\n")


if __name__ == '__main__':
	main()
