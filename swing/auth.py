from flask import Blueprint, request
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden

from .models import User, db
from .config import Config
from .helpers import hash_password

login_manager = LoginManager()

auth = Blueprint('auth', __name__)


@auth.before_app_first_request
def init_user():
    if Config.INIT_USER_EMAIL and Config.INIT_USER_PASSWORD:
        user = User.query.filter_by(email=Config.INIT_USER_EMAIL).first()

        if not user:
            password = hash_password(Config.INIT_USER_PASSWORD)
            user = User(
                email=Config.INIT_USER_EMAIL,
                hashed_password=password,
                active=True)

            db.session.add(user)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return 'Already logged in'

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

    return 'Logged in'


@auth.route('/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        return 'Not logged in'

    logout_user()

    return 'Logged out'
