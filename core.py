#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: core
# purpose: ランダムフォレストを用いて雲海の発生を予測する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import sys
import os
import numpy as np
import pandas as pd
import pickle
import math
import time
import machine as mc
from datetime import datetime as dt
from datetime import timedelta as td

import feature
import amedas.download as amd
import amedas.html_parser as amp
import timeKM

# 何日前のデータまで取るか
days = 6
wait_seconds = 0.1                        # たまにプロキシ？ファイヤウォール？が通信をカットするのでその対策.ほとんど意味がなかったが。。


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるディレクトリの絶対パス



def replace(data_list):
    """ 文字列の要素からなるリストを走査して、都合の悪い文字を削除して返す
    不正文字データの処理はfeature.get_weather_dict()がやってくれるはずだが、、、なんで作ったんだっけ？@2019-01
    """
    new_data = []
    for mem in data_list:
        if "×" == mem:
            new_data.append("nan")
        elif " ]" in mem:
            new_data.append(mem.replace(" ]", ""))
        elif "]" in mem:
            new_data.append(mem.replace("]", ""))
        elif " )" in mem:
            new_data.append(mem.replace(" )", ""))
        elif ")" in mem:
            new_data.append(mem.replace(")", ""))
        else:
            new_data.append(mem)
    return new_data


def get_passed_amedas_data(node_obj, date, term):
    """ dateを起点として、term日分の観測データをダウンロードして返す
    ただし、dateを起点とした過去のデータを返す。
    過去の観測データ用です。
    """
    lines = []
    # 過去データを入手
    for i in range(1, term):
        print("--wait some seconds--")
        time.sleep(wait_seconds)        # たまにプロキシ？ファイヤウォール？が通信をカットするのでその対策
        _date = date - td(days=i)
        now = dt.now()
        if _date.year == now.year and _date.month == now.month and _date.day == now.day: # 現時点の観測データは対応していない
            continue
        print(_date)
        html_txt = node_obj.get_data(_type="hourly", date=_date)
        if html_txt is None:
            print("--can't download--")
            continue
        html_lines = html_txt.split("\n")
        data = amp.get_data(html_lines, _date)
        data = [replace(x) for x in data]
        #print(data)
        lines += [",".join(x) for x in data]
    return lines


def get_amedas_data_typeB(node_obj, date):
    """ 気象庁の気象データを取得して返す（簡易な観測局用）
    """
    # 過去のデータを取得
    lines = get_passed_amedas_data(node_obj, date, days)
    # 最新のデータを入手
    _date = dt.now() + td(days=1)
    if date.year == _date.year and date.month == _date.month and date.day == _date.day:
        html_txt = node_obj.get_data(_type="real-time")
        html_lines = html_txt.split("\n")
        data = amp.get_data(html_lines, dt.now())
        data = [replace(x) for x in data]
        print(data)
        # 最新の観測データは過去の観測データとフォーマットが異なるので、整形する
        # 降水量と気温を入れ替える
        dummy = []
        for mem in data:
            x = mem.pop(3)
            mem.insert(2, x)
            dummy.append(mem)
        data = dummy
        """
        for i in range(len(data)):
            x = data[i][1]
            y = data[i][2]
            data[i][1] = y
            data[i][2] = x
        """
        # 風速と風向を入れ替える
        dummy = []
        for mem in data:
            x = mem.pop(5)
            mem.insert(4, x)
            dummy.append(mem)
        data = dummy
        # 無い観測データ項目を追加
        data = [y + ["", ""] for y in data]
        #print(data)

        # join時にエラーが出ないように全てを文字列化
        dummy = []
        for x in data:
            x = [str(y) for y in x]
            dummy.append(x)
        data = dummy
        #print(data)
        lines += [",".join(x) for x in data]
        #print(lines)
    return lines



def get_amedas_data_typeA2(node_obj, date):
    """ 気象庁の気象データを取得して返す（簡易な観測局用）
    """
    # 過去のデータを取得し、文字列のリストとして返す
    lines = get_passed_amedas_data(node_obj, date, days)

    # 最新のデータを入手
    _date = dt.now() + td(days=1)
    if date.year == _date.year and date.month == _date.month and date.day == _date.day:
        html_txt = node_obj.get_data(_type="real-time")
        #with open("hogehoge.txt", "w", encoding="utf-8-sig") as fw: # debug
        #    fw.write(html_txt)
        html_lines = html_txt.split("\n")
        data = amp.get_data(html_lines, dt.now())
        data = [replace(x) for x in data]
        data = np.array(data)
        columns = data[0]
        columns = ["海面" + c if "気圧" in c else c for c in columns]

        df = pd.DataFrame(data[2:], columns=columns)   # dataframeに変換
        df = df.replace("", np.nan)                    # 未計測部分をnanに置換
        df = df.replace("休止中", np.nan)
        df["気温"] = df["気温"].astype(np.float64)  # 型の変換
        df["湿度"] = df["湿度"].astype(np.float64)
        df["海面気圧"] = df["海面気圧"].astype(np.float64)
        nan = [float("nan")] * len(df)             # 未掲載データをnan
        h = node_obj.height
        df["現地気圧"] = df["海面気圧"] * (1 - (0.0065 * h) / (df["気温"] + 0.0065 * h + 273.15))**5.257  # https://keisan.casio.jp/exec/system/1203469826
        df["視程"] = nan
        df["雲量"] = nan
        df["天気"] = nan
        df["降雪"] = nan
        df["積雪"] = nan
        df["全天日射量"] = nan
        df["日照時間"] = nan

        temp = np.array(df["気温"])          # 気温などから水蒸気圧と露点温度を計算する
        humidity = np.array(df["湿度"])
        P_hPa = feature.get_vapor_pressure(humidity, temp)
        df["水蒸気圧"] = P_hPa
        dew_point_temperature = feature.get_dew_point(humidity, temp)
        df["露点温度"] = dew_point_temperature
        df2 = df[["日時", '時刻', "現地気圧", "海面気圧", "降水量", '気温', "露点温度", "水蒸気圧", "湿度", "風速", "風向", "日照時間", "全天日射量", "降雪", "積雪", "天気", "雲量", "視程"]]
        df2 = df2.replace(np.nan, 0.0)

        # join時にエラーが出ないように全てを文字列化
        data = np.array(df2)
        dummy = []
        for x in data:
            x = [str(y) for y in x]
            dummy.append(x)
        data = dummy
        #print(data)
        lines += [",".join(x) for x in data]

    return lines


# 念のために、この関数は保存しておく
def get_amedas_data_typeA(node_obj, date):
    # 過去のデータを取得
    lines = get_passed_amedas_data(node_obj, date, days)
    # 最新のデータを入手
    _date = dt.now() + td(days=1)
    if date.year == _date.year and date.month == _date.month and date.day == _date.day:
        html_txt = node_obj.get_data(_type="real-time")
        #with open("hogehoge.txt", "w", encoding="utf-8-sig") as fw: # debug
        #    fw.write(html_txt)
        html_lines = html_txt.split("\n")
        data = amp.get_data(html_lines, dt.now())
        data = [replace(x) for x in data]
        # 最新の観測データは過去の観測データとフォーマットが異なるので、整形する
        # 気圧を入れ替える
        dummy = []
        for mem in data:
            #print(mem)
            x = mem.pop(8)
            mem.insert(2, x)
            mem.insert(3, "")
            dummy.append(mem)
        data = dummy
        # 降水量と気温を入れ替える
        dummy = []
        for mem in data:
            x = mem.pop(5)
            mem.insert(4, x)
            dummy.append(mem)
        data = dummy
        # 露点温度、蒸気圧の欄を作る
        dummy = []
        for mem in data:
            mem.insert(6, "")
            mem.insert(6, "")
            dummy.append(mem)
        data = dummy
        # 湿度の位置を変える
        dummy = []
        for mem in data:
            x = mem.pop(11)
            mem.insert(8, x)
            dummy.append(mem)
        data = dummy
        """
        for i in range(len(data)):
            x = data[i][1]
            y = data[i][2]
            data[i][1] = y
            data[i][2] = x
        """
        # 風速と風向を入れ替える
        dummy = []
        for mem in data:
            x = mem.pop(10)
            mem.insert(9, x)
            dummy.append(mem)
        data = dummy
        # 無い観測データ項目を追加
        data = [y + ["", "", "", "", "", ""] for y in data]

        # 水蒸気圧を計算する
        dummy = []
        for mem in data:
            P_hPa = ""
            try:
                t = float(mem[5]) # 気温[deg]
                U = float(mem[8]) # 相対湿度[%]
                P_hPa = feature.get_vapor_pressure(U, t)
            except:
                pass
            mem[7] = P_hPa
            dummy.append(mem)
        data = dummy

        # 露点温度
        dummy = []
        for mem in data: # http://d.hatena.ne.jp/Rion778/20121208/1354975888
            dew_point_temperature = ""
            try:
                t = float(mem[5]) # 気温[deg]
                U = float(mem[8]) # 相対湿度[%]
                dew_point_temperature = feature.get_dew_point(U, t)
            except:
                pass
            mem[6] = dew_point_temperature
            dummy.append(mem)
        data = dummy
        #print(data)

        # join時にエラーが出ないように全てを文字列化
        dummy = []
        for x in data:
            x = [str(y) for y in x]
            dummy.append(x)
        data = dummy
        #print(data)
        lines += [",".join(x) for x in data]
    return lines


def get_amedas_data(node_obj, date):
    """ アメダスの観測データを返す
    含まれる情報別に、ダウンロード後の文字列解析に使う関数を使い分けている。
    """
    if int(node_obj.block_no) > 47000:
        return get_amedas_data_typeA2(node_obj, date)
    else:
        return get_amedas_data_typeB(node_obj, date)
    



def predict_unkai(target_date:dt, process_hour:int, save_flag=True):
    print("予測対象日：", target_date)

    # 予報する対象の時刻
    target_time = 23
    if 23 > process_hour >= 16:
        target_time = 16
    
    # アメダスの観測所オブジェクトを作成
    amedas_nodes = amd.get_amedas_nodes()
    #print(amedas_nodes)
    # 特徴ベクトルを生成するオブジェクトの用意
    features_dict = {}
    for block_no in ["47819", "1240", "0962", "47818"]:
        node = amedas_nodes[block_no]
        lines = get_amedas_data(node, target_date)
        weather_data = feature.get_weather_dict(lines)
        _keys = sorted(weather_data.keys())
        for a_key in _keys:
            print(block_no, weather_data[a_key])
        if int(node.block_no) > 47000:
            features_dict[block_no] = [weather_data, feature.index_A]
        else:
            features_dict[block_no] = [weather_data, feature.index_B]
    fg_obj = feature.feature_generator(target_time, features_dict)

    # 機械学習オブジェクトを生成
    clf = mc.load(ROOT_PATH + "/learned_machine/time" + str(target_time))
    print("type ", type(clf))

    # 特徴ベクトルを生成
    _feature = fg_obj.get_feature(target_date)
    _feature = np.array([_feature]) # TensorFlowはnumpy.arrayの2重の入れ子でないと動かない
    print(_feature)

    # 予測を実施
    print("--predict--")
    print("target date: " + str(target_date))
    print("target time: " + str(target_time))
    print("process hur: " + str(process_hour))

    results = []
    #if _feature != None:
    #if not None in _feature:  # Noneがあると計算出来ない
    test = clf.predict(_feature)
    results.append((target_date, test[0], _feature))
    print(test)


    # 予測結果を保存
    if save_flag:
        with open(ROOT_PATH + "/result.csv", "w") as fw:
            for result in results:
                _date, predict_result, _feature = result
                str_feature = [str(x) for x in _feature]
                fw.write(str(dt.now()))
                fw.write(",")
                fw.write(str(_date))
                fw.write(",")
                fw.write(str(predict_result))
                fw.write(",")
                fw.write("$")
                fw.write(",")
                fw.write(",".join(str_feature))
                fw.write("\n")

    return results



def get_date_now():
    """ 現在時刻を基にした、予想日と時間を返す
    """
    # 予測対象日を求める
    _day = dt.now()        # 現在時刻を取得
    if _day.hour >= 16:    # この時刻を過ぎると、翌日の予想を実施する
        _day += td(days=1)
    target_date = dt(year=_day.year, month=_day.month, day=_day.day) 

    # 予測を実行する時刻
    process_hour = _day.hour

    return target_date, process_hour



def main():
    # 予測対象日や時刻の決定
    target_date, process_hour = get_date_now()

    # 予想したい日の日付けを設定
    argvs = sys.argv       # コマンドライン引数を格納したリストの取得
    argc = len(argvs)      # 引数の個数
    if argc >= 2:          # 引数で計算対象の日を渡す
        arg = argvs[1]
        arg += " 0:0:0"    # 時分秒を加える
        t = timeKM.getTime(arg)
        if t != None:
            target_date = t    

    # 予測を実行する時刻を決定する（引数がなければスクリプト実行時の時刻が使われる）
    if argc >= 3:          # 引数で予想実行時刻を渡す（その時刻に雲海が出るかを確認するものではない）
        arg = argvs[2]
        if arg.isdigit():
            process_hour = int(arg)

    # 雲海が出るか予想値の計算
    result = predict_unkai(target_date, process_hour)
    return result



if __name__ == '__main__':
    main()
