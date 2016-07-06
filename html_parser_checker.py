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
import pandas
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



def replace(data_list):
	""" 文字列の要素からなるリストを走査して、都合の悪い文字を削除して返す
	"""
	new_data = []
	for mem in data_list:
		if "×" == mem:
			new_data.append("nan")
		elif "]" in mem:
			new_data.append(mem.replace("]", ""))
		else:
			new_data.append(mem)
	return new_data


with open("hogehoge2.txt", "r", encoding="utf-8-sig") as fr:
	html_txt = fr.read()
	html_lines = html_txt.split("\n")
	data = amp.get_data(html_lines, dt.now())
	print(data)
	for mem in data:
		print(mem)

	data = [replace(x) for x in data]
	for mem in data:
		print(mem)