from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from .config import Config
from .helpers import check_password, hash_password

db = SQLAlchemy()


def make_user(email, password):
    password = hash_password(password)
    user = User(
        email=email,
        hashed_password=password,
        active=True)
    return user


class User(UserMixin, db.Model):
    """
    Model of the user, where the user can log in to
    the system using his email and password.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    hashed_password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def check_password(self, password):
        return check_password(password, self.hashed_password)

    def is_active(self):
        return self.active

    def get_id(self):
        return self.id

    def to_dict(self):
        return {
            'email': self.email
        }


class Chart(db.Model):
    """
    Model of the chart, where every chart is uniquely
    identified by its name and every chart has its owner.
    """
    __tablename__ = 'charts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    user = db.relationship('User', backref=db.backref('charts', lazy=True))

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description
        }


class Release(db.Model):
    """
    Model of the chart release, where each release
    is uniquely identified by its version.
    """
    __tablename__ = 'releases'

    id = db.Column(db.Integer, primary_key=True)
    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), nullable=False)
    version = db.Column(db.String, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    chart = db.relationship('Chart', backref=db.backref('releases', lazy=True))

    def get_name(self):
        return f'{self.chart.name}-{self.version}'

    def to_dict(self):
        return {
            'version': self.version,
            'releaseDate': self.release_date,
            'notes': self.notes,
            'archiveUrl': f'{Config.PUBLIC_URL}/release/{self.get_name()}.zip'
        }
