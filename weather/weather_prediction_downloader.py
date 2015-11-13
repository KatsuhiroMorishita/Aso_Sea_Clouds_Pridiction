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

# ダウンロードする時刻をセット　ここでは、過去も含む
hours = []
for i in range(24): # 気象庁の予報はいつ更新されるか分からない・・・
	hours.append(td(hours=i, minutes=3, seconds=0))
# 次にダウンロードすべき時刻　過去の時刻は全て未来の時刻に更新
_next = []
for mem in hours:
	t = dt(dt.now().year, dt.now().month, dt.now().day, 0, 0, 0) + mem
	if t < dt.now():
		t += td(days=1)
	_next.append(t)
print(_next)


# 既に保存しているファイルと同じものを保存しないための仕掛け
flist = glob.glob('*.csv')
#print(flist)
create_times = [os.stat(fpath).st_mtime for fpath in flist]
#print(create_times)
lasted_fpath = flist[create_times.index(max(create_times))]
txt = ""
with open(lasted_fpath, "r", encoding="utf-8-sig") as fr:
	txt = fr.read()


_hash = hash(txt)
while True:
	for i in range(len(_next)):
		t = _next[i]
		now = dt.now()
		if t <= now:
			print("--try download--")
			print(str(now))
			url = "http://www.jma.go.jp/jp/week/"
			try:
				fetched_dataframes = pandas.io.html.read_html(url) # download
				print("len: ", len(fetched_dataframes))
				size = []
				for k in range(len(fetched_dataframes)):
					size.append(len(str(fetched_dataframes[k])))
				print("size: ", size)
				table = fetched_dataframes[size.index(max(size))]  # 最大のデータ量のファイルを保存
				if _hash != hash(str(table)):                      # 同じ情報は保存しない
					print("--save--")
					table.to_csv("wether_" + now.strftime('%Y_%m_%d_%H%M%S') + ".csv", encoding="utf-8-sig")
					_hash = hash(str(table))
				else:
					print("--same data downloaded--")
			except Exception as e:
				print("--error--")
				print(str(e))
			_next[i] = t + td(days=1)
			#print(_next)
	time.sleep(60)


