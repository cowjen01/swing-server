import os
import re
import bcrypt

version_regex = r'^\d+(?:\.\d+)+$'
name_regex = r'^[a-z]+(?:-[a-z]+)*$'


def contains(callback, lst) -> bool:
    return next((x for x in lst if callback(x)), None) is not None


def is_valid_version(version) -> bool:
    return bool(re.match(version_regex, version))


def is_valid_chart_name(name) -> bool:
    return bool(re.match(name_regex, name))


def is_valid_path(path: str) -> bool:
    return os.path.isdir(path) and os.access(path, os.R_OK)


def list_to_dict(arr):
    return [x.to_dict() for x in arr]


def generate_salt() -> bytes:
    return bcrypt.gensalt()


def hash_password(password: str, salt: bytes) -> str:
    return str(bcrypt.hashpw(bytes(password, encoding='utf8'), salt))


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(bytes(password, encoding='utf8'), bytes(hashed_password, encoding='utf8'))
