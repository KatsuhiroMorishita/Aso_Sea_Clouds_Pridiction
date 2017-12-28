#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: predict
# purpose: 雲海出現を予測する。学習成果の検証用スクリプト。
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import pandas
import pickle
import datetime
import feature
import numpy as np

import machine as mc


def predict(clf, date_list, feature_generator, save=False):
    """ 引数で渡された日付の特徴量を作成して、渡された学習済みの学習器に入力して識別結果を返す
    argvs:
        clf: 機械学習器
        date_list: 処理対象日が格納されたリスト
        feature_generator: 特徴ベクトル生成器（日付を渡すと特徴ベクトルを作成するオブジェクト）
    """
    results = {}
    for _date in date_list:
        #print(_date)
        _feature = feature_generator.get_feature(_date)
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



def predict2(clf, date_list, features_dict, save=False, feature_display=True):
    """ 引数で渡された日付の特徴量を作成して、渡された学習済みの学習器に入力して識別結果を返す
    一度得直ベクトルを作成して、異なる学習器で何度も識別を行う場合に便利です。
    argvs:
        clf: 機械学習器
        date_list: 処理対象日が格納されたリスト
        feature_dict: 日付をキーとして特徴ベクトルが格納された辞書
    """
    results = {}
    for _date in date_list:
        #print(_date)
        date, _feature, label = features_dict[_date]
        #print(_feature)
        if not _feature is None:
            _feature = np.array(_feature) # リストをnumpyのarray型へ変換
            _feature = np.array([_feature, ])
            if feature_display:           # 特徴ベクトルの検討中は表示させたがいいかも
                print(_feature)
            test = clf.predict(_feature)
            results[_date] = test[0]
            print(_date, test)
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
    # 機械学習オブジェクトを生成（復元）
    clf = mc.load(mc.default_path)

    # 特徴生成オブジェクト作成
    fg_obj = feature.feature_generator(23)

    predict(
        clf, 
        date_range(datetime.datetime(2015, 6, 23), datetime.datetime(2015, 10, 24)), 
        fg_obj, 
        True
        )

if __name__ == '__main__':
    main()