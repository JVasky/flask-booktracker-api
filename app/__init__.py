from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_jwt_extended import JWTManager
from . import models, endpoints
from app import config
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
if os.environ.get('FLASK_ENV') == 'development':
    app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES
app.config['JWT_HEADER_TYPE'] = config.JWT_HEADER_TYPE
app.config['JWT_ERROR_MESSAGE_KEY'] = config.JWT_ERROR_MESSAGE_KEY

# set SMTP Settings
app.config['SMTP_SERVER'] = config.SMTP_SERVER
app.config['SMTP_PORT'] = config.SMTP_PORT
app.config['SMTP_USER'] = config.SMTP_USER
app.config['SMTP_PASSWORD'] = config.SMTP_PASSWORD
app.config['SMTP_FROM_EMAIL'] = config.SMTP_FROM_EMAIL

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
jwt = JWTManager(app)
models.init_app(app)
endpoints.init_app(app)

from . import jwt_custom
