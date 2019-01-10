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
import numpy as np
import sklearn.metrics as mtr

import machine as mc
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
    argvs:
        feature_generator: 特徴ベクトル生成器（日付を渡すと特徴ベクトルを作成するオブジェクト）
        terms: 対象期間
        fname: 正解データの記述されたテキストファイル
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
                value = 0      # あまりに欠損が多いので、Twitterを信じるなら出なかったものとして扱ってOKだと思う.
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


# ROC曲線とAUCを求める
def sub_process2(target_dir, feature_generator, terms):
    """ 保存されている学習器を次々と読みだして評価結果をファイルに保存する
    target_dir: str, 学習器が保存されたフォルダ名
    feature_generator: 特徴ベクトルを作成するクラス
    terms: list, 処理期間を格納したリスト。要素はタプル。要素の数は複数あっても良い。
    """
    flist = mc.get_path_list(target_dir) # 学習器のファイルリストを取得
    print(flist)
    if len(flist) == 0:
        print("0 files or dir found.")
        return

    # 正解データと特徴ベクトルを取得
    data = read_correct_and_create_features(feature_generator, terms)
    dates = sorted(data.keys())

    # 正解のカウントと計算条件のチェック
    correct = [int(data[_date][0]) for _date in dates]
    print("correct: ", correct)
    amount_of_positive = correct.count(1)
    amount_of_negative = correct.count(0)
    if amount_of_positive == 0 or amount_of_negative == 0:    # いずれかが0であれば、計算する意味が無い
        print("amount of positive/negative is 0. So, fin.")
        return

    # 評価用に特徴ベクトルを辞書に格納しなおす
    features = np.array([data[_date][2] for _date in dates])  # 特徴を入れた2次元配列

    # 予想結果を格納する
    predicted_result_dict = {}
    for fpath in flist:
        print("--scoring... now target is {0}--".format(fpath))
        clf = mc.load(fpath)    # オブジェクト復元
        y_score = clf.predict(features)
        predicted_result_dict[fpath] = y_score

    # AUCを求め、結果をファイルに保存    
    auc_report = target_dir + "/learned_machine_report_auc.csv"
    y_true = np.array([int(data[_date][0]) for _date in dates])
    auc_max = (0, "")
    with open(auc_report, "w") as fw_auc:
        for fpath in flist:
            y_score = predicted_result_dict[fpath]

            fpr, tpr, thresholds = mtr.roc_curve(y_true, y_score, pos_label=1)   # ftr: false_positive,  tpr: true_positive
            auc = mtr.auc(fpr, tpr)

            fw_auc.write("{0},{1}\n".format(fpath, auc))
            if auc_max[0] < auc:
                auc_max = (auc, fpath)
        fw_auc.write("AUC max:{0},{1}\n".format(auc_max[1], auc_max[0]))
        print("AUC max:", auc_max)



def main_process(target_time, target_dir, terms):
    """ 
    外部からの呼び出しを意識している。
    target_time: str, 予測したい時刻（生成する特徴量の作成に影響する）
    target_dir: str, 学習器が保存されたフォルダ名
    terms: list, 処理期間を格納したリスト。要素はタプル。要素の数は複数あっても良い。    
    """

    # 引数に合わせて使う特徴ベクトル生成関数を変えて、検証する
    fg_obj = feature.feature_generator(target_time)
    sub_process2(target_dir, fg_obj, terms)


def main():
    # 引数の処理
    target_time = ""   # 処理対象の時刻を引数で指定
    target_dir = ""
    argvs = sys.argv   # コマンドライン引数を格納したリストの取得
    print(argvs)
    argc = len(argvs)  # 引数の個数
    if argc > 2:
        target_time = argvs[1]   # 16 or 23
        target_dir = argvs[2]    # 処理対象のフォルダ
    else:
        print("input target-number and target-dir.")
        exit()

    if not os.path.exists(target_dir):
        print("no such directry: ", target_dir)
        exit()

    # 処理対象の制限（処理時間の短縮になるかも）
    terms = [(dt(2018, 4, 1), dt(2019, 1, 5))] 

    main_process(target_time, target_dir, terms)


if __name__ == '__main__':
    main()
