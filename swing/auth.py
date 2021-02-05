from flask import Blueprint, request
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden

from .models import User, db, make_user
from .config import Config

login_manager = LoginManager()

auth = Blueprint('auth', __name__)


@auth.before_app_first_request
def init_user():
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
    if current_user.is_authenticated:
        return current_user.to_dict()

    credentials = request.authorization

    if not credentials:
        raise BadRequest('Missing credentials')

    email = credentials.username
    password = credentials.password

    if not email or not password:
        raise BadRequest('Invalid auth method')

    user = User.query.filter_by(email=email).first()

    if not user:
        raise NotFound('User not found')

    if not user.check_password(password):
        raise Unauthorized('Invalid credentials')

    if not user.is_active():
        raise Forbidden('Account is not active')

    login_user(user)

    return user.to_dict()


@auth.route('/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        return {}

    logout_user()

    return {}
