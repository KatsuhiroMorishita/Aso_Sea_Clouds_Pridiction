# Aso_Sea_Clouds_Pridiction
Pythonで作った阿蘇に雲海が出現するか予想する機械学習器です。

## プロジェクト概要
[こちら](http://katsuhiromorishita.github.io/Aso_Sea_Clouds_Pridiction/)

## 実行環境
開発環境：Mac OSX pyenv Python3.5, Windows Anaconda Python3.5
動作プラットフォーム：Python 3が動作するLinux, Mac, Windows

Pythonのキャッシュファイルが原因でPython 3.5よりも古いバージョンで動作しないことがあります。また、機械学習機を作成したプラットフォームがMacかWindowsかでお使いのマシン上で動作しないこともあります。その場合、ご自身の環境で学習を実行させて学習機を作成してください。

## スクリプトファイルの説明
### よく使う、重要なスクリプト
* feature.py: 気象データと日付を渡すと特徴ベクトルを生成します。
* core.py: うんかいったーにツイートするサーバーが実行するスクリプトです。実行時点で最新の予想値を計算します。
* learning_repeat.py: 数千回の機械学習を行い、その都度学習済みの機械学習機を保存します。同時に生成されるverify_reportには個々の学習機の学習結果が保存され、性能の高い機械学習機が分かります。
* check4learned_machine.py: auto_verify.pyの作成した学習機を読みだして、閾値による判定を実施します。利用する学習機の選択に利用します。

### ライブラリとして使っているスクリプト
* timeKM.py: 時刻関係の処理を行う。
* learning.py: 学習を行う。
* predict.py: 予想を行う。
* create_learning_data.py: 教師データと検証用のデータを作成・保存する。

### その他のスクリプト
* twitter_bot.py: ツイートする。動作テスト用。
* save_the_day_of_sea_of_clouds.py: production.sqlite3から雲海の撮影日情報を取得してテキストファイルに書き出す。

## 補助ツール
* twilog_photo: twilogにアップしているWebカメラの写真をダウンロードする。
* weather: 気象庁発表の天気予報をダウンロードする。
* weather_satellite: 気象庁から気象衛星の写真をダウンロードする。
* web_cam_capt: 配信されているWebカメラ画像をダウンロードする。

## その他のファイルの説明
* amedas_asoOtohime.csv: 阿蘇乙姫のアメダス観測データ。気象庁のサイトから収集した。
* amedas_kumamoto.csv: 熊本市のアメダス観測データ。気象庁のサイトから収集した。
* entry_16.pickle: 16時台の予想に使う学習済み機械学習機のシリアライズ化データ。
* entry_23.pickle: 23時台の予想に使う学習済み機械学習機のシリアライズ化データ。
* unkai_date.csv: 雲海発生実績と学習の検証に使うかどうかのフラグを収めたファイル。
* production.sqlite3: ネットから収集した雲海の撮影日が格納されているデータベース。
