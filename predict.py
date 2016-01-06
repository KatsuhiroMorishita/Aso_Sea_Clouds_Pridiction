#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: predict
# purpose: ランダムフォレストを用いて、雲海出現を予測する。学習成果の検証用スクリプト。
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import pandas
import pickle
from sklearn.ensemble import RandomForestRegressor
import datetime
import feature



def predict(clf, date_list, feature_generation_func, raw_data, save=False):
	""" 引数で渡された日付の特徴量を作成して、渡された学習済みの学習器に入力して識別結果を返す
	"""
	results = {}
	for _date in date_list:
		#print(_date)
		_feature = feature_generation_func(_date, raw_data)
		#print(_feature)
		if _feature != None:
			if not None in _feature:      # Noneを渡すとエラーが帰るので対策
				test = clf.predict(_feature)
				results[_date] = test[0]
				print(_date, test)
			else:                         # 推定ができなくても、ファイルに書き出すことで正解との比較がやりやすい
				print("--feature has None!--")
				print(_feature)
				results[_date] = None
		else:
			print("--feature is None!--") # 殆ど無いんだが、一応対応
			results[_date] = None


	# 予測結果を保存
	if save:
		dates = sorted(results.keys())
		with open("result_temp.csv", "w") as fw:
			for date in dates:
				predict_result = results[date]
				for _ in range(1):            # 複数行出力できるようにしている
					fw.write(str(date))
					fw.write(",")
					fw.write(str(predict_result))
					fw.write("\n")

	return results



def predict2(clf, date_list, features_dict, save=False):
	""" 引数で渡された日付の特徴量を作成して、渡された学習済みの学習器に入力して識別結果を返す
	"""
	results = {}
	for _date in date_list:
		#print(_date)
		date, _feature, label = features_dict[_date]
		#print(_feature)
		if _feature != None:
			if not None in _feature:      # Noneを渡すとエラーが帰るので対策
				test = clf.predict(_feature)
				results[_date] = test[0]
				print(_date, test)
			else:                         # 推定ができなくても、ファイルに書き出すことで正解との比較がやりやすい
				print("--feature has None!--")
				print(_feature)
				results[_date] = None
		else:
			print("--feature is None!--") # 殆ど無いんだが、一応対応
			results[_date] = None


	# 予測結果を保存
	if save:
		dates = sorted(results.keys())
		with open("result_temp.csv", "w") as fw:
			for date in dates:
				predict_result = results[date]
				for _ in range(1):            # 複数行出力できるようにしている
					fw.write(str(date))
					fw.write(",")
					fw.write(str(predict_result))
					fw.write("\n")

	return results


def date_range(date_start, date_end):
	""" 指定された範囲の日付のリストを作成する
	"""
	ans = []
	_date = date_start 
	while _date <= date_end:
		ans.append(_date)
		_date += datetime.timedelta(days=1)
	return ans



def main():
	# 機械学習オブジェクトを生成
	clf = RandomForestRegressor()
	with open('entry_temp.pickle', 'rb') as f:# 学習成果を読み出す
		clf = pickle.load(f)               # オブジェクト復元

	# 気象データの読み込み
	weather_data_Aso = feature.read_weather_data("amedas_aso.csv", len(feature.index_A))
	weather_data_Otohime = feature.read_weather_data("amedas_asoOtohime.csv", len(feature.index_B))
	#print(weather_data_Aso)
	#print(weather_data_Otohime)
	raw_data = [weather_data_Aso, weather_data_Otohime]

	predict(\
		clf, \
		date_range(datetime.datetime(2015, 6, 23), datetime.datetime(2015, 10, 24)), \
		feature.create_feature23, \
		raw_data, \
		True)

if __name__ == '__main__':
	main()