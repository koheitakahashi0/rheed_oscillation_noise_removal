# RHEED ノイズ除去アプリ

RHEED（反射高速電子回折）データのノイズを、Savitzky-Golay フィルタ＋スパイク除去で処理するWebアプリです。

## 主な機能
- `.txt` データファイルのアップロード
- 測定時間、フィルタパラメータの指定
- 処理結果の可視化とCSV出力

## 実行方法（ローカル）
```bash
pip install -r requirements.txt
streamlit run app.py
