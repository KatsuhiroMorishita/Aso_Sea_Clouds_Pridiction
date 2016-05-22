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
	def __init__(self, feature_generator, terms, fname_observational_data="unkai_date.csv"):
		""" 
		arg:
			terms: 対象期間
		"""
		self._feature_generator = feature_generator
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
		lines = []
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
				self._bad_date.append(date) # あまりに欠損が多いので、Twitterを信じるなら出なかったものとして扱ってOKだと思う.
				#self._unknown_date.append(date)
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
				_feature = self._feature_generator.get_feature(_date) # 特徴ベクトルを作る
				#print(_feature)
				if not _feature is None:
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
		verify_date = []                       # 検証用のデータを学習に使わないように記憶
		verify_ratio = 0.0#0.5                     # ベリファイに使う割合
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
		#print("verify: ", verify_date)

		# 雲海が出たデータ数と出なかったデータ数を調整して、教師データを作成
		teacher_arr = []
		for _date in self._good_feature_set:   # verifyに使われず、かつ雲海の出現した日のデータはすべて使う
			if _date in verify_date:
				continue
			teacher_arr.append(self._all_feature_set[_date])
		#print("teacher good: ", teacher_arr)
		# 雲海が出なかった日のデータを格納する
		zero_ratio = 4.0                   # 雲海が出た（=1）に対する、雲海が出ない（=0）の割合
		use_amount = int(len(teacher_arr) * zero_ratio) # 教師データに含める、雲海が出なかった日のデータ数
		if len(self._bad_feature_set) - (len(self._verify_bad_date) - len(bad_date_copy)) < use_amount:     # 雲海の出現日数よりも非出現日数が少ない場合、非出現データは全て使う
			use_amount = len(self._bad_feature_set) - (len(self._verify_bad_date) - len(bad_date_copy))     # 本気でやるなら偽陽性・偽陰性の許容量に合わせて教師データ数は決めるべき
		count = 0
		use_date4bad = []
		bad_dates = copy.copy(self._bad_date) # 確実に出なかった日のデータを使う
		while count < use_amount:
			if len(bad_dates) <= 0:
				break
			i = random.randint(0, len(bad_dates) - 1)
			_date = bad_dates.pop(i)
			if _date in verify_date:# and _date in use_date4bad:
				continue
			teacher_arr.append(self._bad_feature_set[_date])
			use_date4bad.append(_date)
			count += 1
		bad_dates = list(self._bad_feature_set.keys()) # 足りない場合に、出ていない可能性のある日を加える
		while count < use_amount:
			if len(bad_dates) <= 0:
				break
			i = random.randint(0, len(bad_dates) - 1)
			_date = bad_dates.pop(i)
			if _date in verify_date and _date in use_date4bad:
				continue
			teacher_arr.append(self._bad_feature_set[_date])
			use_date4bad.append(_date)
			count += 1
		#print("teacher bad: ", use_date4bad)
		#exit()
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
