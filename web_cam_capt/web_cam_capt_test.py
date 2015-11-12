import sys
import urllib.request
import re

def download(url, path):
    fp = urllib.request.urlopen(url)
    local = open(path + re.sub(r'[:\\\/]', '_', url), 'wb');
    local.write(fp.read());
    local.close()
    fp.close()

download("http://www.webtv-aso.net/lv/liveimg/image.jpg", "./");

