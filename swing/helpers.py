import os
import re
from werkzeug.security import check_password_hash, generate_password_hash


version_regex = r'^\d+(?:\.\d+)+$'
name_regex = r'^[a-z]+(?:-[a-z]+)*$'
zip_regex = r'^[a-zA-Z0-9\-]+\.zip'


def is_valid_filename(filename) -> bool:
    return bool(re.match(zip_regex, filename))


def is_valid_version(version) -> bool:
    return bool(re.match(version_regex, version))


def is_valid_chart_name(name) -> bool:
    return bool(re.match(name_regex, name))


def is_valid_path(path: str) -> bool:
    return os.path.isdir(path) and os.access(path, os.R_OK)


def list_to_dict(arr):
    return [x.to_dict() for x in arr]


def hash_password(password: str) -> str:
    return generate_password_hash(password, salt_length=12)


def check_password(password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, password)


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
