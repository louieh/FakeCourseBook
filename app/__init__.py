from flask import Flask
from flask_moment import Moment

from config import config

moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))
    config[config_name].init_app(app)

    moment.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
