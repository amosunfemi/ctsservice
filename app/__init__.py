from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from flask.ext.restful import Api
from config import basedir
import os



app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
api = Api(app)

apimanager = APIManager(app, flask_sqlalchemy_db=db)



lm = LoginManager()
lm.init_app(app)
oid = OpenID(app, os.path.join(basedir, 'tmp'))

dburl = app.config.get('SQLALCHEMY_DATABASE_URI')

dburlcba = app.config.get('SQLALCHEMY_DATABASE_CBA_URI')

