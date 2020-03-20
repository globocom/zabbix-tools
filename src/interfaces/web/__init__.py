from config import Config
from flask import Flask
from flask_moment import Moment
import os

moment = Moment()
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = APP_SECRET_KEY
    moment.init_app(app)

    return app