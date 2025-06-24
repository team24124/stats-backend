from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
import logging

app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

# Setup console logging
if not app.debug:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

app.logger.setLevel(logging.INFO)