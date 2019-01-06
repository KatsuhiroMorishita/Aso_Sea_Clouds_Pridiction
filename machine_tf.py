#!usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------
# 機械学習器のインターフェイス. TensorFlow用.
# memo: Python3.5.1 on pyenv on Macにて動作確認。
#       2019-01-06追記　おそらく、今はもう動かないし実装が古い。
# author: Katsuhiro Morishita
# created: 2016-05-05
# license: MIT
#-------------------------------------------
from skflow import TensorFlowDNNClassifier as ml
import skflow
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
		_path = "av_entry_temp_{0:05d}".format(i)
		i += 1
		yield _path


def new():
	""" 初期化した機械学習オブジェクトを返す
	"""
	clf = ml(hidden_units=[40, 20, 15, 10, 20, 10, 20, 10], n_classes=2, learning_rate = 0.05, steps=5000) # TensorFlow
	return clf
	"""
	def my_model(X, y):
		#This is DNN with 10, 20, 10 hidden layers, and dropout of 0.5 probability.
		layers = skflow.ops.dnn(X, [10, 20, 10, 20, 15, 10], keep_prob=0.5)
		return skflow.models.logistic_regression(layers, y)

	clf = skflow.TensorFlowEstimator(model_fn=my_model, n_classes=2)
	return clf
	"""


path_generator = _get_new_path()
def save(clf, dir_path):
	""" 機械学習オブジェクトを保存する
	"""
	_path_list = [dir_path, next(path_generator)]
	_path = create_dir(_path_list)
	clf.save(_path)
	return


def load(dir_path):
	""" 機械学習オブジェクトをファイルから復元する
	"""
	print("--target--", dir_path)
	clf = ml.restore(dir_path)
	return clf


def get_path_list(base):
	""" 機械学習オブジェクトをのファイルまたはフォルダ一覧を取得する
	"""
	#_group = set(["gaph.pgtxt", "model-200.meta", "", "", "", ""]) # ファイル内容の凶器を使うならと思ったけど面倒なので放置
	flist = glob.glob(base + "/*")
	ans = []
	for fpath in flist:
		if os.path.isdir(fpath):
			ans.append(fpath)
	print("--targets--", ans)
	ans = [os.path.abspath(x) for x in ans]
	return ans


