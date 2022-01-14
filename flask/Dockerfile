From python:3
# USER root

COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip

# psycopg2(PostgreSQLクライアント)のインストール
RUN pip install psycopg2

# pip install psycopg2 を使うため
RUN apt install libpq-dev

RUN pip install -r requirements.txt

# RUN python app.py
CMD [ "python", "flask/app/app.py" ]