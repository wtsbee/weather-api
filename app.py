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
    df = pd.read_csv("static/csv/" + city + ".csv", encoding="SHIFT_JIS")
    # 10年分のデータを集計
    sumd = {} # 辞書型を初期化
    for row in df.iterrows():
        ymd = row[1]["年月日"]
        md = re.sub(r'\d{4}\/', '', ymd) # 月/日だけにする
        # 年を閏年の2016年で仮置きする
        md = '2016/' + md
        if not (md in sumd):
            sumd[md] = [0, 0]

        # 列の値を加算する --- (*1)
        for i in range(1, 3):
            sumd[md][i - 1] += row[1][i]
    
    # 表として出力するための処理 --- (*2)
    df = pd.DataFrame.from_dict(sumd).T
    df.columns = ("降水量の合計(mm)","最高気温(℃)")

    df_r = df.reset_index()
    df_r = df_r.rename(columns = {'index':'日付'})

    header = df_r.columns.tolist() # DataFrameのカラム名の1次元配列のリスト
    record = df_r.values.tolist() # DataFrameのインデックスを含まない全レコードの2次元配列のリスト

    # 年月日でソートする
    record = sorted(record, key=lambda x: datetime.strptime(x[0], "%Y/%m/%d"))

    for i in range(len(record)):
        record[i][0] = record[i][0].replace('2016/', '')
        record[i][1] =  round(record[i][1]/10, 1)
        record[i][2] =  round(record[i][2]/10, 1)

    return jsonify({"header": header, "record": record})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8000, debug=False)
