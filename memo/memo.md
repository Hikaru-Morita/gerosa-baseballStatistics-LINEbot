## メモ

### ローカルで LINEdeveloper から webhook する方法
まずサーバーをローカルで起動する
```bash
flask run
```
次に ngrok で公開する
(flask run のデフォルトが 5000 番ポートなので 5000 を指定)
```bash
ngrok http 5000
```
結果
![](./img_forMemo/ngrok_url.png)

上記の https://~.ngrok.io をコピーし、LINE Developers 内 Messaging API 内の webhook URL にペーストし Verify をクリック( Use webhook にチェックを入れる)
![](./img_forMemo/webhook_settings.png)

この時の注意点は /callback を末尾に付け忘れないようにする
当然だがなにも付け足さない場合は / に POST リクエストが飛んでしまう

### docker の使い方
(まだ flask コンテナができただけ)

カレントディレクトリの Dockerfile からイメージをビルドする
```bash
docker build .
```

次にビルドしたイメージにタグを付ける
```bash
docker tag "image_id" linebot gerosa_linebot_python:1.0
```

タグ名を指定してイメージからコンテナを立ち上げる方法
(flaskが5000番ポートなので5000を指定)
```bash
docker run -i -t -p 5000:5000 gerosa_linebot_python:1.0 /bin/bash
```

ローカルディレクトリを指定しマウントしてコンテナを立ち上げる方法
```bash
docker run -i -t -p 5000:5000 -v /home/moritta/working/gerosa-baseballStatistics-LINEbot:/linebot gerosa_linebot_python:1.0 /bin/bash
```

立ち上がっているコンテナに入る方法は
```bash
docker ps
```
でコンテナIDを確認して exec で入る
(bin/bash はシェルにホストにあるbashを指定している)
```bash
docker exec -it コンテナID bin/bash
```

余談だが使わないイメージをまとめて削除するにはこれ
```bash
docker image prune
```

### docker コンテナで flask サーバーを運用する場合の注意
コンテナ内でサーバーを立てる場合は**必ず**下記のコマンドで実行する
```bash
python app.py
```
以前使っていた
```bash
flask run
```
だと flask コード内の
```python
app.run('host=0.0.0.0')
```
の引数で指定したものが反映されないので問題が起きる

flask run を使いたいのならオプションで指定する
```bash
flask  run --host=0.0.0.0
```

そもそも host=0.0.0.0 に設定する理由は外部からアクセスするため、
ホストからコンテナ内へのアクセスは外部アクセスなのでデフォルトでは不可能

### pip install について
```bash
pip install psycopg2    
```
ができなかったため https://qiita.com/b2bmakers/items/d1b0db5966ac145b0e29 
を参照し
```bash
sudo apt install libpq-dev
```
を実行したところできた

### psql について
psql コンテナ内で db に入る方法
```bash
psql -U admin
```
admin は docker-compose 内で指定している

#### auth 関連設定の参照ページ
- [line developer](https://developers.line.biz/console/provider/1656608676)
- [ngrok](https://dashboard.ngrok.com/get-started/setup)

#### ローカル(ubuntu) での開発での参考元
- [サンプルプログラムが動くまで：qiita](https://qiita.com/suigin/items/0deb9451f45e351acf92)
- [ngrok の使い方：個人ブログ](https://parashuto.com/rriver/tools/secure-tunneling-service-ngrok)

#### 参考元
- [川口さんの LINEBOT_資料.pdf](/home/moritta/Downloads/LINEBOT_資料.pdf)
- [奥山の LINEBot](https://github.com/Masaki-Okuyama/Random-number-LINEbot)
- [MessageAPI リファレンス](https://developers.line.biz/ja/reference/messaging-api/)
- [flask ドキュメント](https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/index.html)
<!-- - []() -->

#### docker-compose 参照元
- [](https://qiita.com/kiyokiyo_kzsby/items/bea738fa210216c5ea65)

-https://qiita.com/kiyokiyo_kzsby/items/bea738fa210216c5ea65