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
from sklearn.ensemble import RandomForestClassifier
import datetime
import feature

# 解析対象期間
date_start = datetime.datetime(2015, 6, 26)
date_end   = datetime.datetime(2015, 8, 8)

# 機械学習オブジェクトを生成
clf = RandomForestClassifier()

# 学習成果を読み出す
with open('entry.pickle', 'rb') as f:
	clf = pickle.load(f)               # オブジェクト復元


# 気象データの読み込み
weather_data_Aso = feature.read_weather_data("fusion_aso_test.csv", len(feature.index_A))
weather_data_Otohime = feature.read_weather_data("fusion_asoOtohime_test.csv", len(feature.index_B))
#print(weather_data_Aso)
#print(weather_data_Otohime)


# 日付けをズラしながら、予想結果をストア
results = []
_date = date_start 
while _date <= date_end:
	#print(_date)
	_feature = feature.create_feature(_date, weather_data_Aso, weather_data_Otohime)
	#print(_feature)
	if _feature != None:
		if not None in _feature:      # ランダムフォレスト自体は欠損に強いはずだが、欠損があるとエラーが出たので対策
			test = clf.predict(_feature)
			results.append((_date, test[0]))
			print(_date, test)
	_date += datetime.timedelta(days=1)


# 予測結果を保存
with open("result.csv", "w") as fw:
	for result in results:
		_date, predict_result = result
		for _ in range(5):            # Googleのスプレッドシートに合わせて、4行出力する
			fw.write(str(_date))
			fw.write(",")
			fw.write(str(predict_result))
			fw.write("\n")
