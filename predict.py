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



def predict(clf, date_start, date_end, feature_generation_func, raw_data):
	# 日付けをズラしながら、予想結果をストア
	results = {}
	_date = date_start 
	while _date <= date_end:
		#print(_date)
		_feature = feature_generation_func(_date, raw_data)
		#print(_feature)
		if _feature != None:
			if not None in _feature:      # ランダムフォレスト自体は欠損に強いはずだが、欠損があるとエラーが出たので対策
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
		_date += datetime.timedelta(days=1)


	# 予測結果を保存
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
		datetime.datetime(2015, 6, 23), \
		datetime.datetime(2015, 10, 24), \
		feature.create_feature23, \
		raw_data\
		)

if __name__ == '__main__':
	main()