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
from sklearn import preprocessing
import numpy as np
import machine as mc


def read_training_data(teaching_file_path):
    # 学習に必要な教師データを読み出す
    data = pandas.read_csv(teaching_file_path, na_values='None')
    data = data.dropna()

    #print(data)
    x = (data.iloc[:, :-1]).values    # transform to ndarray
    y = (data.iloc[:, -1:]).values
    y = np.ravel(y)                    # transform 2次元 to 1次元 ぽいこと
    #print(y)
    return (x, y)


def learn(teaching_data):
    # 学習データの用意
    x, y = teaching_data
    clf = mc.new()                     # 学習器の新規作成
    #X = preprocessing.StandardScaler().fit_transform(trainFeature)  # 使った方が良いとは思うが、とりあえず放置
    
    # 学習実行と学習成果を保存
    clf.fit(x, y)

    # 学習結果を確認
    score = clf.score(x, y)    # 学習データに対する、適合率
    #print(clf.feature_importances_)                    # 各特徴量に対する寄与度を求める

    return clf, score


def main():
    training_data = read_training_data("teaching_data.csv")
    clf, score = learn(training_data, mc.default_path)
    mc.save(clf, "learnd_machine_temp")

if __name__ == '__main__':
    main()