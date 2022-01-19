from flask import Flask, Response, request, abort
from flask_sqlalchemy import SQLAlchemy

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

SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@psql:5432/gerosa_linebot'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
# 'postgresql://admin:admin@psql:5432/gerosa_linebot' は 'postgresql://[ユーザ名]:[パスワード]@[コンテナ名]:[ポート番号]/[データベース名]'

gerosa_db = SQLAlchemy(app)
# gerosa_db.create_all()
# gerosa_db.session.commit()

# ファイルから取得
# 後々環境変数に変更
json_file = open('./flask/app/secret.json', 'r')
channel_json = json.load(json_file)
line_bot_api = LineBotApi(channel_json['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(channel_json['LINE_CHANNEL_SECRET'])

def get_connection():
    return psycopg2.connect(DATABASE_URL)


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
    result = do_sql_select("SELECT * FROM gerosa-linebot WHERE userID='%s';" % user_id)

    if result:  # データベースに登録されているユーザか判定
        # 登録済み
        line_bot_api.reply_message(
            event.reply_token,
            (
                TextSendMessage('登録済み'),
            )
        )
    else:
        # 未登録
        do_sql_other("INSERT INTO gerosa-linebot VALUES ('%s', '右', '右');" % user_id)
        line_bot_api.reply_message(
            event.reply_token,
            (
                TextSendMessage('未登録'),
            )
        )
        # データベースに登録されていないユーザーは登録する

    line_bot_api.reply_message(
        event.reply_token,
        # TextSendMessage(text=event.message.text)
        TextSendMessage(text='to mo yo')
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0') # 外部からアクセスする設定