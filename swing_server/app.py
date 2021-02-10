from flask import Flask, json
from flask_session import Session
from werkzeug import exceptions

from .api import main as main_blueprint
from .auth import auth as auth_blueprint, login_manager
from .config import Config, validate_config
from .models import db
from .errors import InvalidConfigError

session = Session()


def create_app():
    """
    Create Flask application and setup all configurations.
    Before the application instance is returned, provide validation
    of the configuration settings. All exceptions are handled in one
    place and returned as a JSON object with an error description.
    """
    app = Flask(__name__)

    try:
        validate_config()
    except InvalidConfigError as e:
        print(e.message)

    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = Config.SESSION_TYPE
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_FILE_DIR'] = Config.SESSION_FILE_DIR
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SESSION_PERMANENT'] = Config.SESSION_PERMANENT

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

    db.create_all(app=app)

    return app
