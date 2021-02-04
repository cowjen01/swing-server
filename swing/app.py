import logging

from flask import Flask, json
from flask_session import Session
from werkzeug import exceptions

from .models import db
from .config import Config, validate_config
from .auth import auth as auth_blueprint, login_manager
from .api import main as main_blueprint

logging.basicConfig(level=logging.DEBUG)
session = Session()


def create_app():
    app = Flask(__name__)

    validate_config()

    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    app.config['SESSION_SQLALCHEMY'] = db
    app.secret_key = Config.SECRET_KEY

    db.init_app(app)
    session.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    @app.errorhandler(exceptions.HTTPException)
    def handle_exception(e):
        response = e.get_response()
        response.data = json.dumps({
            'code': e.code,
            'name': e.name,
            'description': e.description,
        })
        response.content_type = 'application/json'
        return response

    return app
