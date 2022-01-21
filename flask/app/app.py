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
json_file.close()

# DB とコネクションを生成
def get_connection():
    return psycopg2.connect(
        dbname = 'gerosa_linebot',
        user = 'admin',
        password = 'admin',
        host = 'psql',
        port = 5432
    )

# SQL文 select を実行
def do_sql_select(sql):
    result = None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchall()
    return result

# SQL文 select 以外を実行
def do_sql_other(sql):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


# テキストメッセージを受信
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = str(event.source.user_id)
    result = do_sql_select("SELECT * FROM player WHERE id='%s';" % user_id)

    if result:  # データベースに登録されているユーザか判定

        if '選手一覧' in event.message.text:
            replyAllPlayers(user_id)
        
        elif '試合一覧' in event.message.text:
            replyAllGames(user_id)

        elif '試合成績:打者':
            colums = event.message.text.split(",")
            replyAllBats(user_id,colums[1])


        elif '試合結果追加' in event.message.text:
            registerGame(event)
        
    else:
        # 未登録
        # 規定の形式なら登録する
        colums = event.message.text.split(",")
        registerPlayer(colums,user_id,event)


# 新規ユーザーを登録する
def registerPlayer(colums, user_id, event):
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
                TextSendMessage('選手登録を始めます'),
                TextSendMessage('登録のため\n \"登録,{フルネーム},{背番号},{右or左}打ち,{右or左}投げ\" \nを投稿して下さい \n ("," の後にスペースを空けないで下さい)'),
                TextSendMessage('例： 登録,森田光,22,右打ち,右投げ'),
            )
        )

# 打者成績を登録
def registerBat(event):
    colums = event.message.text.split(",")

    do_sql_other(
        "INSERT INTO player VALUES ('{0}', '{1}', '{2}');"
        .format(colums[0], colums[1], colums[2])
    )

# 試合を登録する
def registerGame(event):
    # "東京Muse,20220118,3-2"
    result = event.message.text.split(":")
    colums = result[1].split(",")
    colums_score = colums[2].split("-")
    do_sql_other(
        "INSERT INTO player VALUES ('{0}', '{1}', '{2}', '{3}');"
        .format(colums[0], colums[1], colums_score[0], colums_score[1])
    )
    
    for player in getPlayers():
        line_bot_api.push_message(player[0], TextSendMessage(text='{0}'.format(player[1])))


def replyAllPlayers(user_id):
    # LINE BOTのreplyMessage(応答メッセージ)は
    # 送信されたメッセージ１つに付きreply tokenが発行され
    # それを使ってBOTが返信するという仕組みになっている
    # そのため line_bot_api.push_message を用いる
    for player in getPlayers():
        line_bot_api.push_message(user_id, TextSendMessage(text='{0}'.format(player[1])))

def replyAllGames(user_id):
    for game in getGames():
        line_bot_api.push_message(user_id, 
            TextSendMessage(text='{0},{1},{2},{3}'.format(game[0],game[1],game[2],game[3]))
        )

def replyAllBats(user_id, game_id):
    team_name = do_sql_select('SELECT team_name FROM game WHERE game.id = {0};'.format(str(game_id)))
    for bat in getBats(game_id):
        player_name = do_sql_select('SELECT full_name FROM player WHERE player.id = \'{0}\';'.format(str(bat[0])))
        line_bot_api.push_message(user_id, 
            TextSendMessage(text="{0} : {1}打数".format(player_name[0],bat[2]))
        )


def getPlayers():
    result = do_sql_select("SELECT id,full_name FROM player;")
    return result

def getGames():
    result = do_sql_select("SELECT id,team_name,game_day,result FROM game;")
    return result

def getBats(game_id):
    result = do_sql_select('SELECT * FROM bat WHERE bat.game_id = {0};'.format(str(game_id)))
    print(result,flush=True)
    return result

# def getPersonalBats(user_id, game_id):

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


if __name__ == "__main__":
    app.run(host='0.0.0.0') # 外部からアクセスする設定