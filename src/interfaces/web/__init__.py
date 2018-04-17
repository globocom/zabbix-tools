from config import Config
from flask import Flask
from flask_moment import Moment

moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'ab21d71a-4247-11e8-842f-0ed5f89f718b'
    moment.init_app(app)

    return app