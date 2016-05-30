#!/usr/bin/env python
# -*- coding: utf-8 -*-
# purpose: 気象庁の天気予報を定期的にpandasでダウンロードする
# created: 2015-10-
# license: MIT
import pandas
from datetime import datetime as dt
from datetime import timedelta as td
import time
import glob
import os

import amedas.download as amd
import amedas.html_parser as amp
import timeKM


def get_amedas_data_type(node_obj):
	html_txt = node_obj.get_data(_type="real-time")
	html_lines = html_txt.split("\n")
	data = amp.get_data(html_lines, dt.now())
	#print(data)
	return data

def download():
	now = dt.now()
	amedas_nodes = amd.get_amedas_nodes()
	for block_no in ["47819", "1240", "0962", "47818"]:
		node = amedas_nodes[block_no]
		lines = get_amedas_data_type(node)
		print(block_no, node.name)
		print(lines)
		out = []
		for mem in lines:
			out.append("\t".join(mem))
		out = "\n".join(out)
		with open("amedas_" + block_no + "_" + node.name + "_" + now.strftime('%Y_%m_%d_%H%M%S') + ".tsv", "w", encoding="utf-8-sig") as fw:
			fw.write(out)


# ダウンロードする時刻をセット　ここでは、過去も含む
hours = []
for i in range(24): # 気象庁の予報はいつ更新されるか分からない・・・
	hours.append(td(hours=i, minutes=5, seconds=0))
# 次にダウンロードすべき時刻　過去の時刻は全て未来の時刻に更新
_next = []
for mem in hours:
	t = dt(dt.now().year, dt.now().month, dt.now().day, 0, 0, 0) + mem
	if t < dt.now():
		t += td(days=1)
	_next.append(t)
print(_next)



while True:
	for i in range(len(_next)):
		t = _next[i]
		now = dt.now()
		if t <= now:
			print("--try download--")
			print(str(now))
			try:
				download()
			except Exception as e:
				print("--error--")
				print(str(e))
			_next[i] = t + td(days=1)
			#print(_next)
	time.sleep(60)


