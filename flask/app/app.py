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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@psql:5432/gerosa_linebot'
gerosa_db = SQLAlchemy(app)
gerosa_db.create_all()
gerosa_db.session.commit()

# ファイルから取得
# 後々環境変数に変更
json_file = open('./flask/app/secret.json', 'r')
channel_json = json.load(json_file)
line_bot_api = LineBotApi(channel_json['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(channel_json['LINE_CHANNEL_SECRET'])

@app.route("/")
def hello_world():
    return "hello world!"

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run(host='0.0.0.0')