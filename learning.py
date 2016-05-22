#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: learning
# purpose: 雲海の出現を予測するために機械学習器を学習させる
# author: Katsuhiro MORISHITA, 森下功啓
# memo: 読み込むデータは、1行目にラベルがあり、最終列に層名が入っていること。
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import pandas
import skflow
from sklearn import preprocessing
import numpy as np
import machine as mc


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
	# 学習データの用意
	trainFeature, trainLabel = teaching_data
	hoge = [np.array(x) for x in trainFeature] # リストをnumpyのarray型へ変換
	trainFeature = np.array(hoge)
	trainLabel = np.array(trainLabel)
	clf = mc.new()                     # 学習器の新規作成
	X = trainFeature
	#X = preprocessing.StandardScaler().fit_transform(trainFeature)
	clf.fit(X, trainLabel)             # 学習実行

	# 学習成果を保存
	mc.save(clf, save_file_path)

	# 学習結果を確認のために表示
	print(X[2:3])
	test = clf.predict(X[2:3])          # 試しに一つ確認
	print(test)
	result = clf.score(X, trainLabel)	# 学習データに対する、適合率
	print(result)
	#print(clf.feature_importances_)	                # 各特徴量に対する寄与度を求める

	return clf


def main():
	training_data = read_training_data("teaching_data.csv")
	learn(training_data, mc.default_path)

if __name__ == '__main__':
	main()