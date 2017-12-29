#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: create_learning_data
# purpose: 雲海の出現予想に必要な学習データ（教師データ）を作成する
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import datetime
from datetime import datetime as dt
from datetime import timedelta as td
import feature
import copy
import random
import timeKM


def get_unkai(_date, unkai_dates):
    """ 当日に雲海が出たかどうかのフラグ
    該当するなら、数字の1を返す。
    """
    if _date in unkai_dates:
        return 1
    else:
        return 0


def get_unkai_pre1(_date, unkai_dates):
    """ 当日の翌日朝に雲海が出たかどうかのフラグ
    該当するなら、数字の2を返す。
    """
    _date += datetime.timedelta(days=1)
    if _date in unkai_dates:
        return 1
    else:
        return 0


def get_unkai_pre2(_date, unkai_dates):
    """ 当日の翌々日朝に雲海が出たかどうかのフラグ
    該当するなら、数字の4を返す。
    """
    _date += datetime.timedelta(days=2)
    if _date in unkai_list:
        return 1
    else:
        return 0



class  teacher_creator():
    def __init__(self, feature_generator, terms, fname_observational_data="unkai_date.csv"):
        """ 
        arg:
            terms: 対象期間
        """
        self._fg = feature_generator
        self._term = terms
        self._all_feature_set = {}
        self._good_date = []
        self._bad_date = []
        self._verify_good_date = []  
        self._verify_bad_date = []
        

        # 雲海発生データを読み込む　未観測も含めて取得する
        lines = []
        with open(fname_observational_data, "r", encoding="utf-8-sig") as fr:
            lines = fr.readlines()
        for line in lines:
            line = line.rstrip()
            date, value, verify_flag = line.split("\t")
            date = timeKM.getTime(date + " 0:0:0")

            if self._check_date(terms, date) == False:
                continue
            if value == "1":                   # 雲海が出た
                self._good_date.append(date)
                if verify_flag == "v":
                    self._verify_good_date.append(date)
            elif value == "0":                 # 雲海が出てない（もしくは、出ていても良い景色ではない）
                self._bad_date.append(date)
                if verify_flag == "v":
                    self._verify_bad_date.append(date)
            elif value == "x":                 # 雲海が出たか不明
                self._bad_date.append(date)    # あまりに欠損が多いので、Twitterを信じて出なかったものとして扱ってOKだと思う.
        #print(self._good_date)

        # 教師データを作る
        for date_start, date_end in terms:
            _date = date_start
            while _date <= date_end:
                _feature = self._fg.get_feature(_date)         # 特徴ベクトルを作る

                if not _feature is None:
                    point = get_unkai(_date, self._good_date)
                    self._all_feature_set[_date] = (_date, _feature, point)
                _date += datetime.timedelta(days=1)


    def _check_date(self, terms, date):
        """ 日付が期間内にあるかを確認する
        """
        for date_start, date_end in terms:
            if date_start <= date <= date_end:
                return True
        return False

    def create_dataset(self):
        """ 学習データと検証データを作成する
        """

        # 雲海が出たデータ数と出なかったデータ数を調整して、教師データを作成
        teacher_arr = []
        for _date in self._good_date:   # 雲海の出現した日のデータはすべて使う
            teacher_arr.append(self._all_feature_set[_date])
        print("--good size in teacher--", len(teacher_arr))

        # 雲海が出なかった日のデータを格納する
        ratio = 4.0                                # 雲海が出た（=1）に対する、雲海が出ない（=0）の割合
        use_amount = int(len(teacher_arr) * ratio) # 教師データに含める、雲海が出なかった日のデータ数（雲海の出現日数よりも非出現日数が少ない場合は、データ数はこれ以下になるので注意）
        count = 0
        bad_dates = copy.copy(self._bad_date)      # 雲海が出なかった日のデータを使う（阿蘇においては最近の観測分だけ使われる）
        while count < use_amount:
            if len(bad_dates) <= 0:
                break
            i = random.randint(0, len(bad_dates) - 1)
            _date = bad_dates.pop(i)
            teacher_arr.append(self._all_feature_set[_date])
            count += 1
        print("--bad size in teacher--", count)

        dates = [_date for _date, one_teaching_data, flag in teacher_arr]
        x = [one_teaching_data for _date, one_teaching_data, flag in teacher_arr]
        y = [flag for _date, one_teaching_data, flag in teacher_arr]

        # 過学習判定用のデータ抽出
        pass
        test_data = {}

        return (test_data, dates, x, y)

    def save_teacher(self, save_name_teacher="teaching_data.csv", save_name_verify="verify_data.csv"):
        """ 学習データと検証データを作成してを保存しつつ、作った教師データを返す
        """
        print("--save_teacher()--")
        test_data, teacher_dates, x, y = self.create_dataset()

        # 過学習判定用のデータをファイルに保存
        with open(save_name_verify, "w", encoding="utf-8") as fw:
            if len(test_data) > 0:
                dates = sorted(test_data.keys())
                for _date in dates:
                    flag = test_data[_date]
                    fw.write(str(_date) + ",")
                    fw.write(str(flag))
                    fw.write("\n")

        # 教師データをファイルに保存
        if len(x) > 0:
            with open(save_name_teacher, "w", encoding="utf-8") as fw:
                length = len(x[0])             # 要素数を把握
                fw.write("date,")
                label = ["V" + str(i) for i in range(length)] # ラベル
                fw.write(",".join(label))
                fw.write(",label")
                fw.write("\n")
                for _date, one_teaching_data, flag in zip(teacher_dates, x, y):
                    one_teaching_data = [str(x) for x in one_teaching_data]
                    one_teaching_data = ",".join(one_teaching_data)
                    fw.write(str(_date) + ",")
                    fw.write(one_teaching_data)
                    fw.write(",{0}".format(flag))
                    fw.write("\n")
        return (test_data, teacher_dates, x, y)

    def get_all_features(self):
        return copy.copy(self._all_feature_set)



def main():
    # 処理の対象期間（過去のデータに加えて、最新の観測データも加えるので、タプルで期間を指定する）
    #terms = [(dt(2004, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2016, 1, 4))]
    terms = [(dt(2015, 6, 23), dt(2015, 11, 30))]

    # 特徴ベクトルを作成する関数
    fg_obj = feature.feature_generator(23)

    # 特徴ベクトルを作成して保存
    tc = teacher_creator(fg_obj, terms)
    tc.save_teacher()






if __name__ == '__main__':
    main()
