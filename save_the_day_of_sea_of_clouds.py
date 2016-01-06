#!usr/bin/python3
# -*- coding: utf-8 -*-
#----------------------------------------
# name: save_the_day_of_sea_of_clouds
# purpose: Web上にアップされた写真を基に作成されたDBから、雲海の出た日付けを抜き出してファイルに保存する
# author: Katsuhiro MORISHITA, 森下功啓
# memo: 読み込むデータは、1行目にラベルがあり、最終列に層名が入っていること。
# created: 2015-08-08
# lisence: MIT
#----------------------------------------
import sqlite3

print("-テーブル名の取得-")
con = sqlite3.connect("production.sqlite3")
cur = con.cursor()
cur.execute("select name from sqlite_master where type='table'")
for catalog in cur.fetchall():
	tableName = catalog[0]
	columnIndex = 0
	print(tableName)

print("-カラム名の取得-")
c = con.execute("select * from unkai_photos")
desc = c.description
for columnIndex in range(len(desc)):
	columnName = desc[columnIndex][0]
	print(columnName)


print("-テーブル内のデータを取得-")
result = []
rows = c.fetchall()
for row in rows:
	_date = row[-5]
	print(_date)
	result.append(_date)
con.close()

# 雲海の出た日を保存
with open("temp_unkai_date.csv", "w") as fw:
	for mem in result:
		fw.write(mem)
		fw.write("\n")


