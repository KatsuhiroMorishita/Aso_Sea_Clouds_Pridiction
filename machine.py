#!usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------
# 機械学習器のインターフェイス. ランダムフォレスト用.
# author: Katsuhiro Morishita
# created: 2016-05-05
# license: MIT
#-------------------------------------------
from sklearn.ensemble import RandomForestRegressor as ml # RF
import pickle
import glob
import os


default_path = "./model"


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


def _get_new_path():
	""" 保存する際に利用できるファイル名・フォルダ名を返すジェネレータ
	"""
	i = 0
	while True:
		_path = "av_entry_temp_{0:05d}.pickle".format(i)
		i += 1
		yield _path


def new():
	""" 初期化した機械学習オブジェクトを返す
	"""
	clf = ml(max_features="auto", max_depth=40, n_estimators=150, n_jobs=2) # RF
	return clf


path_generator = _get_new_path()
def save(clf, dir_path):
	""" 機械学習オブジェクトを保存する
	"""
	print(dir_path)
	create_dir([dir_path])
	_fpath = dir_path + "/" + next(path_generator)
	with open(_fpath, 'wb') as f:
		pickle.dump(clf, f)
	return


def load(path):
	""" 機械学習オブジェクトをファイルから復元する
	"""
	clf = new()
	with open(path, 'rb') as f:     # 学習成果を読み出す
		clf = pickle.load(f)        # オブジェクト復元
	return clf


def get_path_list(base):
	""" 機械学習オブジェクトをのファイルまたはフォルダ一覧を取得する
	"""
	#_group = set(["gaph.pgtxt", "model-200.meta", "", "", "", ""]) # ファイル内容の凶器を使うならと思ったけど面倒なので放置
	flist = glob.glob(base + "/*.pickle")
	ans = []
	for fpath in flist:
		if os.path.isfile(fpath):
			ans.append(fpath)

	return ans