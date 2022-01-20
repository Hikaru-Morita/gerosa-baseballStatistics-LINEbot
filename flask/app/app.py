from typing import Text
from flask import Flask, Response, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import json
import os               # 環境変数を読み込む
import psycopg2         # PostgreSQL を使う
import numpy as np      # 数値計算

app = Flask(__name__)


# ファイルから取得
# 後々環境変数に変更
json_file = open('./flask/app/secret.json', 'r')
channel_json = json.load(json_file)
line_bot_api = LineBotApi(channel_json['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(channel_json['LINE_CHANNEL_SECRET'])

def get_connection():
    return psycopg2.connect(
        dbname = 'gerosa_linebot',
        user = 'admin',
        password = 'admin',
        host = 'psql',
        port = 5432
    )

def do_sql_select(sql):
    result = None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchall()
    return result

def do_sql_other(sql):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

# Line bot の webhook 用
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'



# テキストメッセージを受信
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = str(event.source.user_id)

    result = do_sql_select("SELECT * FROM player WHERE id='%s';" % user_id)

    if result:  # データベースに登録されているユーザか判定
        # 登録済み
        line_bot_api.reply_message(
            event.reply_token,
            (
                TextSendMessage('登録済み'),
                TextSendMessage(result[0][0]),
                TextSendMessage(result[0][1]),
            )
        )
    else:
        # 未登録
        # 規定の形式なら登録する
        colums = event.message.text.split(",")
        if colums[0] == "登録":
            try:
                # データベースに登録されていないユーザーは登録する
                do_sql_other("INSERT INTO player VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(user_id, colums[1], colums[2], colums[3], colums[4]))
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    (
                        TextSendMessage('例に従って登録を行って下さい'),
                        TextSendMessage('例： 登録,森田光,22,右打ち,右投げ'),
                    )
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    (
                        TextSendMessage('登録完了'),
                    )
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                (
                    TextSendMessage('未登録'),
                    TextSendMessage('登録のため\n \"登録,{フルネーム},{背番号},{右or左}打ち,{右or左}投げ\" \nを投稿して下さい \n ("," の後にスペースを空けないで下さい)'),
                    TextSendMessage('例： 登録,森田光,22,右打ち,右投げ'),
                )
            )

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     # TextSendMessage(text=event.message.text)
    #     TextSendMessage(text='to mo yo')
    # )

if __name__ == "__main__":
    app.run(host='0.0.0.0') # 外部からアクセスする設定