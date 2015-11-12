#!/usr/bin/env python
# -*- coding: utf-8 -*-
# web_cam_capt
# purpose: Web TV阿蘇が設置しているWebカメラの配信画像をダウンロードする
#          http://www.webtv-aso.net/lv/
# author: Katsuhiro Morishita
# created: 2015-11-08
# license: MIT
import pandas
from datetime import datetime as dt
from datetime import timedelta as td
import time
import sys
import urllib.request
import re



def download(url, path):
    """ 指定されたパスでデータをバイナリ保存する（画像に限らない）
    """
    fp = urllib.request.urlopen(url)
    with open(path, 'wb') as fw:
        fw.write(fp.read())
    fp.close()






# ダウンロードする時刻をセット　ここでは、過去も含む
times = []
for hour in range(24):             # 
	for minute in range(0,60,10):  # 
		#for second in range(0, 60, 10):
		second = 0
		times.append(td(hours=hour, minutes=minute, seconds=second))
# 次にダウンロードすべき時刻　過去の時刻は全て未来の時刻に更新
_next = []
for mem in times:
	t = dt(dt.now().year, dt.now().month, dt.now().day, 0, 0, 0) + mem
	if t < dt.now():
		t += td(days=1)
	_next.append(t)
print(_next)


_hash = None
while True:
	for i in range(len(_next)):
		t = _next[i]
		now = dt.now()
		if t <= now:
			print("--try download--")
			print(str(now))
			target_time = now# - td(minutes=30)
			_time = target_time.strftime("%Y%m%d%H%M")
			print(_time)
			url = "http://www.webtv-aso.net/lv/liveimg/image.jpg"
			print(url)
			try:
				download(url, _time + ".jpg");
			except Exception as e:
				print("--error--")
				print(str(e))
			_next[i] = t + td(days=1)
			#print(_next)
	time.sleep(10)


