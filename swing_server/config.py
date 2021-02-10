from os import environ, path

from dotenv import load_dotenv

from .helpers import create_directory
from .storage import StorageType
from .errors import InvalidConfigError

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    DATABASE_URI = environ.get('DATABASE_URI')
    PUBLIC_URL = environ.get('PUBLIC_URL', 'http://localhost:5000')
    STORAGE_TYPE = environ.get('STORAGE_TYPE', StorageType.LOCAL)
    STORAGE_LOCAL_DIR = environ.get('STORAGE_LOCAL_DIR')
    INIT_USER_EMAIL = environ.get('INIT_USER_EMAIL')
    INIT_USER_PASSWORD = environ.get('INIT_USER_PASSWORD')
    SESSION_TYPE = environ.get('SESSION_TYPE', 'sqlalchemy')
    SESSION_FILE_DIR = environ.get('SESSION_FILE_DIR')
    SESSION_PERMANENT = (environ.get('SESSION_PERMANENT', 'True') == 'True')


def validate_config():
    """
    Make validation of the environment variables.
    """
    if not Config.SECRET_KEY:
        raise InvalidConfigError('Secret key can not be empty.')

    if not Config.DATABASE_URI:
        raise InvalidConfigError('Database URI can not be empty.')

    if Config.STORAGE_TYPE not in [StorageType.LOCAL]:
        raise InvalidConfigError('Requested storage type is not valid.')

    if Config.STORAGE_TYPE == StorageType.LOCAL:
        if not Config.STORAGE_LOCAL_DIR:
            raise InvalidConfigError('Local storage directory can not be empty.')

        try:
            create_directory(Config.STORAGE_LOCAL_DIR)
        except OSError as e:
            raise InvalidConfigError('Local storage directory could not be created.')

    if Config.SESSION_TYPE == 'filesystem':
        if not Config.SESSION_FILE_DIR:
            raise InvalidConfigError('Directory for the session files can not be empty.')

        try:
            create_directory(Config.SESSION_FILE_DIR)
        except OSError as e:
            raise InvalidConfigError('Directory for the session files could not be created.')

    if Config.INIT_USER_EMAIL and not Config.INIT_USER_PASSWORD:
        raise InvalidConfigError('Initial user password can not be empty.')
