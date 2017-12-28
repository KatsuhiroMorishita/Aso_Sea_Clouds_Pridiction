#!/usr/bin/env python
# -*- coding: utf-8 -*-
# twilog_img_downloader
# author: Katsuhiro Morishita
# purpose: twilogを見ながら判定するのが面倒なので、画像をまとめてダウンロードする。
# created: 2015-12-26
# license: MIT
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime as dt
from datetime import timedelta as td



start = dt(year=2017, month=7, day=1)
end = dt(year=2017, month=12, day=27)

origin_url = "http://twilog.org/unkaitterbot/date-"

# ダウンロードに必要なURLを作成する
urls = {}
t = start
while t < end:
    date_str = t.strftime('%y%m%d')
    date_str2 = t.strftime('%Y%m%d')
    print(date_str)
    urls[date_str2] = origin_url + date_str
    t += td(days=1)

# 画像をダウンロードしつつ、保存する
dates = sorted(urls.keys())
for date in dates:
    url = urls[date]
    download_urls = []
    r = requests.get(url)
    #print(r.content)
    soup = BeautifulSoup(r.content, "html.parser")
    #print(soup)
    links = soup.findAll('img', class_="tl-image")
    #print(links)

    # URLの抽出
    print("--**--")
    for link in links:
        #print(link)
        #print(type(link))
        href = link.get('src')
        #print(href)

        if "jpg" and "twimg" in href:
            href = href.replace(":small", "")
            print(href)
            download_urls.append(href)

    # ファイルのダウンロード
    for i in range(len(download_urls)):
        download_url = download_urls[i]
        time.sleep(1)
        file_name = date + "_" + str(len(download_urls) - i) + ".jpg"
        r = requests.get(download_url)

        # ファイルの保存
        if r.status_code == 200:
            f = open(file_name, 'wb')
            f.write(r.content)
            f.close()