#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 気象庁の天気予報を定期的にpandasでダウンロードする
import pandas
from datetime import datetime as dt
from datetime import timedelta as td
import time

hours = []
for i in range(24):
	hours.append(td(hours=i, minutes=1))
_next = []
for mem in hours:
	t = dt(dt.now().year, dt.now().month, dt.now().day, 0, 0, 0) + mem
	if t < dt.now():
		t += td(days=1)
	_next.append(t)


while True:
	for i in range(len(_next)):
		t = _next[i]
		now = dt.now()
		if t <= now:
			print("--download--")
			url = "http://www.jma.go.jp/jp/week/"
			fetched_dataframes = pandas.io.html.read_html(url)
			table = fetched_dataframes[5]
			table.to_csv("wether_" + now.strftime('%Y_%m_%d_%H%M%S') + ".csv", encoding="utf-8-sig")
			_next[i] = t + td(days=1)
	print(_next)
	time.sleep(60)


