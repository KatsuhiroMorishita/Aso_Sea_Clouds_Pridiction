# Aso_Sea_Clouds_Pridiction
Pythonで作った阿蘇に雲海が出現するか予想する機械学習器です。

## プロジェクト概要
[こちら](http://katsuhiromorishita.github.io/Aso_Sea_Clouds_Pridiction/)

## 実行環境
開発環境：Mac OSX pyenv Python3.5, Windows Anaconda Python3.5  
動作プラットフォーム：Python 3が動作するLinux, Mac, Windows

Pythonのキャッシュファイルが原因でPython 3.5よりも古いバージョンで動作しない場合、キャッシュフォルダを削除して下さい。また、機械学習機を作成したプラットフォームがMacかWindowsかでお使いのマシン上で動作しない場合は、ご自身の環境で学習を実行させて学習機を作成してください。

## スクリプトファイルの説明
### よく使う、重要なスクリプト
* feature.py: 気象データを基に特徴ベクトルを生成します。
* core.py: うんかいったーにツイートするサーバーが実行するスクリプトです。実行時点で最新の予想値を計算します。
* learning_repeat.py: 学習を複数行い、学習が完了するとそのつど学習済みの機械学習機をファイルに保存します。
* check4learned_machine.py: learning_repeat.pyの作成した学習機を読みだして、閾値による判定を実施します。
* machine_rf.py: ランダムフォレスト用の機械学習器スクリプトです。利用する際は、machine.pyにコピペします。
* machine_tf.py: TensorFlow用の機械学習器スクリプトです。学習済みのオブジェクトを使う場合で学習時からフォルダを移動させる場合は、フォルダ内のテキストファイル「checkpoint」内のパスを指定しなおして下さい。

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
* amedas_realtime_store: 気象庁が発表する準リアルタイムの観測データを帝国にダウンロードすることで更新タイミングを調べるツール。

## その他のファイルの説明
* amedas_0962.csv: 島原のアメダス観測データ。気象庁のサイトから収集した。学習に使います。
* amedas_1240.csv: 阿蘇乙姫のアメダス観測データ。
* amedas_47819.csv: 熊本市のアメダス観測データ。
* amedas_47818.csv: 雲仙岳のアメダス観測データ。
* ./learned_machine/time16: 16時台の予想に使う学習済み機械学習機の保存データ。ランダムフォレスト用ならファイル、TnesorFlor用ならフォルダです。
* ./learned_machine/time23: 23時台の予想に使う学習済み機械学習機の保存データ。
* unkai_date.csv: 雲海発生実績と学習の検証に使うかどうかのフラグを収めたファイル。学習に使います。
* production.sqlite3: ネットから収集した雲海の撮影日が格納されているデータベース。学習に使います。
