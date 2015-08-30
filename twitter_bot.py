#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: twitter_bot
# purpose: 雲海発生予測を毎日繰り返し、結果をツイートする
# author: Katsuhiro MORISHITA, 森下功啓
# created: 2015-08-26
# lisence: MIT
#----------------------------------------
from datetime import datetime as dt
from datetime import timedelta as td
from requests_oauthlib import OAuth1Session
import time
import core


def post_tweet(msg):
	# キーを読み込み
	lines = []
	with open("../tweet_key.txt", "r") as fr: # キーはGitHubにはアップしない
		lines = fr.readlines()
		lines = [line.rstrip() for line in lines]
	CK, CS, AT, AS = lines # Consumer Key, Consumer Secret, Access Token, Accesss Token Secert

	# ツイート投稿用のURL
	url = "https://api.twitter.com/1.1/statuses/update.json"

	# ツイート本文
	params = {"status": msg}

	# OAuth認証で POST method で投稿
	twitter = OAuth1Session(CK, CS, AT, AS)
	req = twitter.post(url, params = params)

	# レスポンスを確認
	if req.status_code == 200:
	    print ("--tweet OK--")
	else:
	    print ("--tweet Error code: {0}--".format(req.status_code))


done = False
while True:
	date = dt.now()
	print(date, "checking now...")
	if done == False and (date.hour == 23 or date.hour == 16) and 59 > date.minute > 20:
		print("--call core main--")
		result = core.main()
		done = True
		msg = "【unkaitter bot test】{0}に雲海が出る尤度は{1}です。".format((date + td(days=1)).strftime("%Y-%m-%d"), result[0][1])
		print(msg)
		post_tweet(msg)
		print("--done--")
	if date.hour == 0 or date.hour == 17:
		print("--ready--")
		done = False
	time.sleep(60)




