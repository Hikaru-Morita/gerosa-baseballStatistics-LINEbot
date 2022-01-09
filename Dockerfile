From python:3
# USER root

COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip

# psycopg2(PostgreSQLクライアント)のインストール
RUN pip install psycopg2

RUN pip install -r requirements.txt

FROM postgres:11-alpine