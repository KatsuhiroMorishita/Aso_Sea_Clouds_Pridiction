#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: create_learning_data
# purpose: 雲海の出現予想に必要な特徴量を作成する
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


def get_unkai(_date, unkai_list):
	""" 当日に雲海が出たかどうかのフラグ
	該当するなら、数字の1を返す。
	"""
	if _date in unkai_list:
		return 1
	else:
		return 0


def get_unkai_pre1(_date, unkai_list):
	""" 当日の翌日朝に雲海が出たかどうかのフラグ
	該当するなら、数字の2を返す。
	"""
	_date += datetime.timedelta(days=1)
	if _date in unkai_list:
		return 2
	else:
		return 0


def get_unkai_pre2(_date, unkai_list):
	""" 当日の翌々日朝に雲海が出たかどうかのフラグ
	該当するなら、数字の4を返す。
	"""
	_date += datetime.timedelta(days=2)
	if _date in unkai_list:
		return 4
	else:
		return 0



class  teacher_creator():
	def __init__(self, raw_data, feature_generation_func, terms):
		""" 
		arg:
			terms: 対象期間
		"""
		self._raw_data = raw_data
		self._feature_generation_func = feature_generation_func
		self._term = terms
		self._unkai_date_list = []
		self._unkai_good = []
		self._unkai_bad = []

		# 雲海の出た日付けのリストを読み込む
		with open("unkai_date.csv", "r", encoding="utf-8-sig") as fr:
			lines = fr.readlines()
			for line in lines:
				line = line.rstrip()
				date = line + " 0:0:0"
				t = timeKM.getTime(date)
				self._unkai_date_list.append(t)
		#print(self._unkai_date_list)

		# 教師データを作る
		#unkai_label = ["st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7"]
		#unkai_label = ["st0", "st1"]
		unkai_label = ["0", "1"]
		for date_start, date_end in terms:
			_date = date_start
			while _date <= date_end:
				#print(_date)
				_feature = self._feature_generation_func(_date, raw_data)
				#print(_feature)
				if _feature != None:
					unkai_point = get_unkai(_date, self._unkai_date_list)# + get_unkai_pre1(_date, unkai_date_list) + get_unkai_pre2(_date, unkai_date_list)
					_unkai = unkai_label[unkai_point]
					if _unkai == unkai_label[0]:
						self._unkai_bad.append((_date, _feature, _unkai)) # 時刻と一緒にタプルで保存
					else:
						self._unkai_good.append((_date, _feature, _unkai))
				_date += datetime.timedelta(days=1)

	def save_teacher(self, save_name="teaching_data.csv"):
		""" 学習データを保存する
		今はファイル名を返しているが、特徴ベクトルと正解ラベルを返していいかと思う。
		"""
		print("--save_teacher()--")

		# 雲海が出たデータ数と、出なかったデータ数を調整
		teaching_data = copy.copy(self._unkai_good)
		bad_data = copy.copy(self._unkai_bad)
		use_amount = int(len(self._unkai_good) * 5.0)
		if len(bad_data) < use_amount:     # 雲海の出現日数よりも非出現日数が少ない場合、非出現データは全て使う
			use_amount = len(bad_data)     # ただし、本気でやるなら偽陽性・偽陰性の許容量に合わせて教師データ数は決めるべき
		for _ in range(use_amount):
			i = random.randint(0, len(bad_data) - 1)
			new_member = bad_data.pop(i)
			teaching_data.append(new_member)
		#print(teaching_data)


		# 教師データをファイルに保存
		if len(teaching_data) > 0:
			with open(save_name, "w", encoding="utf-8") as fw:
				length = len(teaching_data[0][1])             # 要素数を把握
				fw.write("date,")
				label = ["V" + str(i) for i in range(length)] # ラベル
				fw.write(",".join(label))
				fw.write(",label")
				fw.write("\n")
				for _date, one_teaching_data, flag in teaching_data:
					one_teaching_data = [str(x) for x in one_teaching_data]
					one_teaching_data = ",".join(one_teaching_data)
					fw.write(str(_date) + ",")
					fw.write(one_teaching_data)
					fw.write(",{0}".format(flag))
					fw.write("\n")
		return save_name



def main():
	# 気象データの読み込み
	raw_data = feature.read_raw_data()

	# 処理の対象期間（過去のデータに加えて、最新の観測データも加えるので、タプルで期間を指定する）
	terms = [(dt(2005, 3, 10), dt(2013, 8, 1)), (dt(2015, 6, 23), dt(2015, 8, 24))]

	# 特徴ベクトルを作成する関数
	feature_func = feature.create_feature16

	# 特徴ベクトルを作成して保存
	tc = teacher_creator(raw_data, feature_func, terms)
	tc.save_teacher()






if __name__ == '__main__':
	main()
