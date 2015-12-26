import sys
import urllib.request
import re

def download(url, path):
    fp = urllib.request.urlopen(url)
    local = open(path + re.sub(r'[:\\\/]', '_', url), 'wb')
    local.write(fp.read())
    local.close()
    fp.close()

download("http://www.jma.go.jp/jp/gms/imgs/0/infrared/1/201511041400-00.png", "./");


# テスト
from datetime import datetime as dt
now = dt.now()
print("--try download--")
print(str(now))
minute = int(now.minute / 30) * 30
_time = now.strftime("%Y%m%d%H") + str("{0:02d}".format(minute))
print(_time)
url = "http://www.jma.go.jp/jp/gms/imgs/0/infrared/1/" + _time +"-00.png"
print(url)
download(url, "./");
