from flask_sqlalchemy import SQLAlchemy
from app.app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin_pass@postgres-server:5432/gerosa_linebot'
db = SQLAlchemy(app)