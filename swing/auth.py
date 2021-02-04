from flask import Blueprint, request
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden

from .models import User

login_manager = LoginManager()

auth = Blueprint('auth', __name__)


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
