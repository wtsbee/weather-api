from flask import Flask, jsonify, request, render_template
from datetime import datetime
import pandas as pd
import re

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/", methods=["GET", "POST"])
def post_request():
    # CSVデータを読み込む
    city = request.json["city"]
    from_dt = request.json["from_dt"]
    to_dt = request.json["to_dt"]
    sort_key = request.json["sort_key"]
    # 文字列から日付への変換
    from_dt = datetime.strptime('2016/' + from_dt, "%Y/%m/%d")
    to_dt = datetime.strptime('2016/' + to_dt, "%Y/%m/%d")
    # csvファイルの読み込み
    df = pd.read_csv("static/csv/" + city + ".csv", encoding="SHIFT_JIS")
    # 10年分のデータを集計
    sumd = {} # 辞書型を初期化
    for row in df.iterrows():
        ymd = row[1]["年月日"]
        kousui = row[1]["降水量の合計(mm)"]
        md = re.sub(r'\d{4}\/', '', ymd) # 月/日だけにする
        # 年を閏年の2016年で仮置きする
        md = '2016/' + md
        date_dt = datetime.strptime(md, "%Y/%m/%d")
        if from_dt <= date_dt <= to_dt:
            if not (date_dt in sumd):
                sumd[date_dt] = [0, 0, 0, 0, 0]
            # 列の値を加算する
            for i in range(1, 5):
                sumd[date_dt][i] += row[1][i]
            # 雨の日の場合に1を加算
            if kousui > 0:
                sumd[date_dt][0] += 1
    
    # 表として出力するための処理
    df = pd.DataFrame.from_dict(sumd).T
    df.columns = ("雨の日数(日)","1日の降水量(mm)","最高気温(℃)","最低気温(℃)","平均気温(℃)")

    df_r = df.reset_index()
    df_r = df_r.rename(columns = {'index':'日付'})

    if sort_key == "日付":
        # 日付でソートする
        df_r = df_r.sort_values(by=["日付"] , ascending=True)
    else:
        # ソートキーで並び替え
        df_r = df_r.sort_values(by=[sort_key, "日付"] , ascending=True)

    header = df_r.columns.tolist() # DataFrameのカラム名の1次元配列のリスト
    record = df_r.values.tolist() # DataFrameのインデックスを含まない全レコードの2次元配列のリスト

    for i in range(len(record)):
        record[i][0] = record[i][0].strftime("%m/%d")
        record[i][0] = re.sub('^0', '', record[i][0])
        record[i][0] = re.sub('/0', '/', record[i][0])
        record[i][1] = round(record[i][1])
        if record[i][0] == "2/29":
            record[i][2] = round(record[i][2]/2, 1)
            record[i][3] = round(record[i][3]/2, 1)
            record[i][4] = round(record[i][4]/2, 1)
            record[i][5] = round(record[i][5]/2, 1)
        else:
            record[i][2] = round(record[i][2]/10, 1)
            record[i][3] = round(record[i][3]/10, 1)
            record[i][4] = round(record[i][4]/10, 1)
            record[i][5] = round(record[i][5]/10, 1)

    return jsonify({"header": header, "record": record})

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')
