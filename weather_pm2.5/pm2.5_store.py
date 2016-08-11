#!/usr/bin/env python
# -*- coding: utf-8 -*-
# purpose: PM2.5の予報データを定期的にpandasでダウンロードする
# created: 2016-08-11
# author: Katsuhiro MORISHITA
# license: MIT
import pandas
from datetime import datetime as dt
from datetime import timedelta as td
import time


def download():
	now = dt.now()
	url = "http://sprintars.riam.kyushu-u.ac.jp/forecastj_list_main.html"
	fetched_dataframes = pandas.io.html.read_html(url)
	table = fetched_dataframes[0]
	fname = "amedas_" + now.strftime('%Y_%m_%d_%H%M%S') + ".csv"
	table.to_csv(fname, encoding="utf-8-sig")


# ダウンロードする時刻をセット　ここでは、過去も含む
hours = []
for i in range(24): # 気象庁の予報はいつ更新されるか分からない・・・
	hours.append(td(hours=i, minutes=20, seconds=0))
#hours.append(td(hours=16, minutes=20, seconds=0))
#hours.append(td(hours=23, minutes=20, seconds=0))

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


