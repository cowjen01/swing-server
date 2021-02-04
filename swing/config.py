from os import environ, path
from dotenv import load_dotenv

from .helpers import is_valid_path
from .storage import StorageType

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    DATABASE_URI = environ.get('DATABASE_URI')
    PUBLIC_URL = environ.get('PUBLIC_URL', 'http://localhost:5000')
    STORAGE_TYPE = environ.get('STORAGE_TYPE', StorageType.LOCAL)
    STORAGE_LOCAL_DIR = environ.get('STORAGE_LOCAL_DIR')


def validate_config():
    if not Config.SECRET_KEY:
        raise Exception('Missing SECRET_KEY variable')

    if not Config.DATABASE_URI:
        raise Exception('Missing DATABASE_URI variable')

    if Config.STORAGE_TYPE not in [StorageType.LOCAL]:
        raise Exception('Invalid STORAGE_TYPE variable')

    if Config.STORAGE_TYPE == StorageType.LOCAL:
        if not Config.STORAGE_LOCAL_DIR:
            raise Exception('Missing STORAGE_LOCAL_DIR variable')

        if not is_valid_path(Config.STORAGE_LOCAL_DIR):
            raise Exception('Invalid STORAGE_LOCAL_DIR path')
