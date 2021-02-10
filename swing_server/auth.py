from flask import Blueprint, request
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden

from .config import Config
from .models import User, db, make_user

login_manager = LoginManager()

auth = Blueprint('auth', __name__)


@auth.before_app_first_request
def init_user():
    """
    After the Flask application starts, create
    an initial user using environment variables.
    """
    if Config.INIT_USER_EMAIL and Config.INIT_USER_PASSWORD:
        user = User.query.filter_by(email=Config.INIT_USER_EMAIL).first()

        if not user:
            user = make_user(Config.INIT_USER_EMAIL, Config.INIT_USER_PASSWORD)

            db.session.add(user)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['POST'])
def login():
    """
    Make user login using encoded credentials sent in the Authorization
    header of the request. The user's account has to be activated.
    """
    if current_user.is_authenticated:
        return current_user.to_dict()

    credentials = request.authorization

    if not credentials:
        raise BadRequest('Login credentials were not provided.')

    email = credentials.username
    password = credentials.password

    if not email or not password:
        raise BadRequest('Provided credentials have not got a valid format.')

    user = User.query.filter_by(email=email).first()

    if not user:
        raise NotFound(f'No user with email \'{email}\' was found.')

    if not user.check_password(password):
        raise Unauthorized('Provided credentials do not match any account.')

    if not user.is_active():
        raise Forbidden('The account is not activated, so it could not be logged in.')

    login_user(user)

    return user.to_dict()


@auth.route('/logout', methods=['POST'])
def logout():
    """
    Log out currently logged user.
    """
    if not current_user.is_authenticated:
        return {
            'status': 'You are currently not logged in.'
        }

    logout_user()

    return {
        'status': 'You have been logged out.'
    }
