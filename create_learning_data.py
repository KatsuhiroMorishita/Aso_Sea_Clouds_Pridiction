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
	def __init__(self, raw_data, feature_generation_func, terms, fname_observational_data="unkai_date.csv"):
		""" 
		arg:
			raw_data: アメダスの観測データ
			terms: 対象期間
		"""
		self._raw_data = raw_data
		self._feature_generation_func = feature_generation_func
		self._term = terms
		self._good_feature_set = {}
		self._bad_feature_set = {}
		self._all_feature_set = {}
		self._good_date = []
		self._bad_date = []
		self._unknown_date = []
		self._verify_bad_date = []
		self._verify_good_date = []

		# 雲海発生データを読み込む　未観測も含めて取得する
		with open(fname_observational_data, "r", encoding="utf-8-sig") as fr:
			lines = fr.readlines()
		for line in lines:
			line = line.rstrip()
			date, value, verify_flag = line.split("\t")
			date = timeKM.getTime(date + " 0:0:0")
			if self._check_date(terms, date) == False:
				continue
			if value == "1":
				self._good_date.append(date)
				if verify_flag == "v":
					self._verify_good_date.append(date)
			elif value == "0":
				self._bad_date.append(date)
				if verify_flag == "v":
					self._verify_bad_date.append(date)
			elif value == "x":
				self._unknown_date.append(date)
		#print(self._good_date)

		# 教師データを作る
		#unkai_label = ["st0", "st1", "st2", "st3", "st4", "st5", "st6", "st7"]
		#unkai_label = ["st0", "st1"]
		unkai_label = [0, 1]
		for date_start, date_end in terms:
			_date = date_start
			while _date <= date_end:
				if _date in self._unknown_date:       # 未観測とはっきりしている場合は特徴ベクトル生成の対象外
					_date += datetime.timedelta(days=1)
					continue
				#print(_date)
				_feature = self._feature_generation_func(_date, raw_data) # 特徴ベクトルを作る
				#print(_feature)
				if _feature != None:
					unkai_point = get_unkai(_date, self._good_date)# + get_unkai_pre1(_date, unkai_date_list) + get_unkai_pre2(_date, unkai_date_list)
					label = unkai_label[unkai_point]
					if label == unkai_label[0]:
						self._bad_feature_set[_date] = (_date, _feature, label) # 時刻と一緒にタプルで保存
					else:
						self._good_feature_set[_date] = (_date, _feature, label)
					self._all_feature_set[_date] = (_date, _feature, label)
				_date += datetime.timedelta(days=1)
		#print(self._good_feature_set)


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
		# verify用のデータ抽出
		verify_data = {}
		verify_date = []                       # 学習に使わないように記憶
		verify_ratio = 0.5                     # ベリファイに使う割合
		good_date_copy = copy.copy(self._verify_good_date)
		use_amount = int(len(self._verify_good_date) * verify_ratio)
		for _ in range(use_amount):
			i = random.randint(0, len(good_date_copy) - 1)
			_date = good_date_copy.pop(i)
			verify_data[_date] = 1             # 0: 雲海は発生していない, 1: 雲海は発生した
			verify_date.append(_date)
		bad_date_copy = copy.copy(self._verify_bad_date)
		if int(len(bad_date_copy) * verify_ratio) < use_amount:
			use_amount = int(len(bad_date_copy) * verify_ratio)
		for _ in range(use_amount):
			i = random.randint(0, len(bad_date_copy) - 1)
			_date = bad_date_copy.pop(i)
			verify_data[_date] = 0
			verify_date.append(_date)

		# 雲海が出たデータ数と出なかったデータ数を調整して、教師データを作成
		teacher_arr = []
		zero_ratio = 5.0                   # 雲海が出た（=1）に対する、雲海が出ない（=0）の割合
		for _date in good_date_copy:       # 雲海の出現した日のデータはすべて使う
			teacher_arr.append(self._all_feature_set[_date])
		use_amount = int(len(good_date_copy) * zero_ratio)
		if len(self._bad_feature_set) - len(bad_date_copy) < use_amount:     # 雲海の出現日数よりも非出現日数が少ない場合、非出現データは全て使う
			use_amount = len(self._bad_feature_set) - len(bad_date_copy)     # 本気でやるなら偽陽性・偽陰性の許容量に合わせて教師データ数は決めるべき
		count = 0
		for _date in bad_date_copy:
			teacher_arr.append(self._bad_feature_set[_date])
			count += 1
		bad_dates = list(self._bad_feature_set.keys())
		while count < use_amount:
			i = random.randint(0, len(bad_dates) - 1)
			_date = bad_dates.pop(i)
			if _date in verify_date and _date in bad_date_copy: # bad_date_copyはコピー済みなので省く
				continue
			teacher_arr.append(self._bad_feature_set[_date])
			count += 1
		#print(teacher_arr)
		teacher_dates = [_date for _date, one_teaching_data, flag in teacher_arr]
		teacher_features = [one_teaching_data for _date, one_teaching_data, flag in teacher_arr]
		teacher_flags = [flag for _date, one_teaching_data, flag in teacher_arr]

		return (verify_data, teacher_dates, teacher_features, teacher_flags)

	def save_teacher(self, save_name_teacher="teaching_data.csv", save_name_verify="verify_data.csv"):
		""" 学習データと検証データを作成してを保存する
		"""
		print("--save_teacher()--")
		verify_data, teacher_dates, teacher_features, teacher_flags = self.create_dataset()

		# verify用のデータをファイルに保存
		if len(verify_data) > 0:
			dates = sorted(verify_data.keys())
			with open(save_name_verify, "w", encoding="utf-8") as fw:
				for _date in dates:
					flag = verify_data[_date]
					fw.write(str(_date) + ",")
					fw.write(str(flag))
					fw.write("\n")

		# 教師データをファイルに保存
		if len(teacher_features) > 0:
			with open(save_name_teacher, "w", encoding="utf-8") as fw:
				length = len(teacher_features[0])             # 要素数を把握
				fw.write("date,")
				label = ["V" + str(i) for i in range(length)] # ラベル
				fw.write(",".join(label))
				fw.write(",label")
				fw.write("\n")
				for _date, one_teaching_data, flag in zip(teacher_dates, teacher_features, teacher_flags):
					one_teaching_data = [str(x) for x in one_teaching_data]
					one_teaching_data = ",".join(one_teaching_data)
					fw.write(str(_date) + ",")
					fw.write(one_teaching_data)
					fw.write(",{0}".format(flag))
					fw.write("\n")
		return (verify_data, teacher_dates, teacher_features, teacher_flags)

	def get_all_features(self):
		return copy.copy(self._all_feature_set)



def main():
	# 気象データの読み込み
	raw_data = feature.read_raw_data()

	# 処理の対象期間（過去のデータに加えて、最新の観測データも加えるので、タプルで期間を指定する）
	terms = [(dt(2004, 2, 18), dt(2013, 9, 3)), (dt(2015, 6, 23), dt(2016, 1, 4))]

	# 特徴ベクトルを作成する関数
	feature_func = feature.create_feature16

	# 特徴ベクトルを作成して保存
	tc = teacher_creator(raw_data, feature_func, terms)
	tc.save_teacher()






if __name__ == '__main__':
	main()
