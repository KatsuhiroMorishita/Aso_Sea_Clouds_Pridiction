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
import machine as mc


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
            verify_data, teacher_dates, x, y = None, None, None, None
            if save_flag:
                _save_name_teacher = tag_name + "/av_teaching_data" + tag_name + "_{0:05d}".format(i) + ".csv" # tc.save_teacher(ファイル名)で教師と検証データを保存するときに使う
                _save_name_verify = tag_name + "/av_verify_data" + tag_name + "_{0:05d}".format(i) + ".csv"
                verify_data, teacher_dates, x, y = tc.save_teacher(save_name_teacher=_save_name_teacher, save_name_verify=_save_name_verify) # 毎回、呼び出すたびにデータセットの内容が変わる
            else:
                verify_data, teacher_dates, x, y = tc.create_dataset() # 毎回、呼び出すたびにデータセットの内容が変わる
            features_dict = tc.get_all_features()
            training_data = (x, y)
            

            # 学習と保存
            clf, score = learning.learn(training_data)
            mc.save(clf, tag_name)
            fw.write("{0},{1}\n".format(i, score))

            # 過学習の確認（現状では役に立っていない）
            dates = sorted(verify_data.keys())                   # 学習に使っていない日付
            if len(dates) == 0:
                continue
            result = predict.predict2(clf, dates, features_dict) # 学習に使っていないデータで検証


def main():
    # 引数の処理
    target_time = ""   # 処理対象の時刻を引数で指定
    target_dir = ""
    try_times = 10    # 試行回数
    argvs = sys.argv   # コマンドライン引数を格納したリストの取得
    print(argvs)
    argc = len(argvs)  # 引数の個数
    if argc > 3:
        target_time = argvs[1]      # 16 or 23
        target_dir = argvs[2]       # 結果を保存するフォルダ名
        try_times = int(argvs[3])   # 作成する学習器の数（RFなら2000〜3000が良いと思う）
    else:
        print("input: target-time, target-dir, try-times")
        exit()

    # 教師データ作成の準備
    terms = [(dt(2004, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2018, 3, 31))] # for aso
    #terms = [(dt(2010, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2016, 5, 1))] # for aso
    #terms = [(dt(2015, 6, 23), dt(2016, 2, 1))] # for aso
    #terms = [(dt(2015, 3, 1), dt(2016, 4, 1))] # for chichibu

    _save_flag = False # 検証用にファイルを残したいなら、Trueとする

    # 特徴生成オブジェクト作成
    fg_obj = feature.feature_generator(target_time)
    tc = create_learning_data.teacher_creator(fg_obj, terms, "unkai_date.csv") # 一度メモリ内に教師データを作成するが、時間がかかる。
    process(target_dir, tc, save_flag=_save_flag, try_times=try_times)



if __name__ == '__main__':
    main()
