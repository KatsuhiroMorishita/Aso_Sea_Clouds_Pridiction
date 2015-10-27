#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: learning
# purpose: 雲海の出現を予測するためにランダムフォレストオブジェクトを学習させる
# author: Katsuhiro MORISHITA, 森下功啓
# memo: 読み込むデータは、1行目にラベルがあり、最終列に層名が入っていること。
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import pandas
from sklearn.ensemble import RandomForestRegressor as ml


def read_training_data(teaching_file_path):
	# 学習に必要な教師データを読み出す
	data = pandas.read_csv(teaching_file_path, na_values='None')
	data = data.dropna()

	#print(data)
	features = (data.iloc[:, 1:-1]).values # transform to ndarray
	labels = (data.iloc[:, -1:]).values
	labels = [flatten for inner in labels for flatten in inner] # transform 2次元 to 1次元 ぽいこと
	#print(labels)
	return (features, labels)


def learn(teaching_data, save_file_path):
	# 学習実行
	trainFeature, trainLabel = teaching_data
	clf = ml(max_features="auto")#, max_depth=7)
	clf.fit(trainFeature, trainLabel)

	# 学習成果を保存
	import pickle
	with open(save_file_path, 'wb') as f:
		pickle.dump(clf, f)

	# 学習結果を確認のために表示
	test = clf.predict(trainFeature[2])             # 試しに一つ確認
	print(test)
	result = clf.score(trainFeature, trainLabel)	# 学習データに対する、適合率
	print(result)
	print(clf.feature_importances_)	                # 各特徴量に対する寄与度を求める

	return clf


def main():
	training_data = read_training_data("teaching_data.csv")
	learn(training_data, 'entry_temp.pickle')

if __name__ == '__main__':
	main()