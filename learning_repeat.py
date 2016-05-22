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
import os

import learning
import predict
import feature
import create_learning_data
import timeKM


def create_dir(path_list):
    """ 指定されたパスのディレクトリを作成する
    Argv:
        path_list   <list<str>> 作成するディレクトリ
                        階層を要素とする。
    """
    #print(path_list)
    _dir = ""
    for men in path_list:
        _dir = os.path.join(_dir, men)
        #print(dir)
        if not os.path.isdir(_dir):
            os.mkdir(_dir)
    return _dir


def process(tag_name, tc, save_flag=False, try_times=2000):
	""" 学習とその検証を繰り返して、結果をファイルに保存する
	"""
	_dir = create_dir([tag_name])

	with open(tag_name + "/av_verify_report" + tag_name + ".csv", "w") as fw:
		for i in range(try_times):
			print("--try count: {0}/{1}--".format(i, try_times))

			# 教師データを作成
			verify_data, teacher_dates, teacher_features, teacher_flags = None, None, None, None
			if save_flag:
				_save_name_teacher = tag_name + "/av_teaching_data" + tag_name + "_{0:05d}".format(i) + ".csv" # tc.save_teacher(ファイル名)で教師と検証データを保存するときに使う
				_save_name_verify = tag_name + "/av_verify_data" + tag_name + "_{0:05d}".format(i) + ".csv"
				verify_data, teacher_dates, teacher_features, teacher_flags = tc.save_teacher(save_name_teacher=_save_name_teacher, save_name_verify=_save_name_verify) # 毎回、呼び出すたびにデータセットの内容が変わる
			else:
				verify_data, teacher_dates, teacher_features, teacher_flags = tc.create_dataset() # 毎回、呼び出すたびにデータセットの内容が変わる
			features_dict = tc.get_all_features()
			training_data = (teacher_features, teacher_flags)
			dates = sorted(verify_data.keys())                   # 学習に使っていない日付

			# 学習
			clf = learning.learn(training_data, tag_name)
			result = predict.predict2(clf, dates, features_dict) # 学習に使っていないデータで検証
			
			# 必要なら個別の結果も保存
			if save_flag:
				with open(tag_name + "/av_verify_data" + tag_name + "_{0:05d}".format(i) + "_result.csv", "w") as fw_result:
					for date in dates:
						if date in result:
							try:      # このtryはいらないんじゃないかな・・・
								fw_result.write(str(date))
								fw_result.write(",")
								fw_result.write(str(verify_data[date]))
								fw_result.write(",")
								fw_result.write(str(result[date]))
								fw_result.write("\n")
							except:
								pass

			# 結果の集計
			scale = 10
			zero = [0.000001] * scale # sum()して分母に入れようとしたら、0の時にエラーが出るので0.000001とした
			one = [0.000001] * scale
			for date in dates:
				if date in result:
					try:              # このtryはいらないんじゃないかな・・・
						c = verify_data[date]
						val = c - result[date]
						if int(c) == 0:
							zero[abs(int(val * scale))] += 1
						elif int(c) == 1:
							one[abs(int(val * scale))] += 1
						#print(val)
					except:
						pass

			# 最終結果の一覧ファイルへの保存
			zero = [str(x / sum(zero)) for x in zero] # 正規化
			one = [str(x / sum(one)) for x in one]
			fw.write("{0},".format(i))
			fw.write(",".join(zero))
			fw.write(",,") # Excelで閲覧した時に分離させる
			fw.write(",".join(one))
			fw.write("\n")

def main():
	# 引数の処理
	target_time = ""   # 処理対象の時刻を引数で指定
	target_dir = ""
	try_times = 10    # 試行回数
	argvs = sys.argv   # コマンドライン引数を格納したリストの取得
	print(argvs)
	argc = len(argvs)  # 引数の個数
	if argc > 3:
		target_time = argvs[1]
		target_dir = argvs[2]
		try_times = int(argvs[3])
	else:
		print("input: target-time, target-dir, try-times")
		exit()

	# 教師データ作成の準備
	terms = [(dt(2004, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2016, 5, 1))]
	#terms = [(dt(2010, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2016, 5, 1))]
	#terms = [(dt(2015, 6, 23), dt(2016, 2, 1))]

	_save_flag = False # 検証用にファイルを残したいなら、Trueとする

	# 特徴生成オブジェクト作成
	fg_obj = feature.feature_generator(target_time)
	tc = create_learning_data.teacher_creator(fg_obj, terms, "unkai_date.csv") # 一度メモリ内に教師データを作成するが、時間がかかる。
	process(target_dir, tc, save_flag=_save_flag, try_times=try_times)



if __name__ == '__main__':
	main()
