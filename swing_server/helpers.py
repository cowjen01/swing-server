import os
import re

from werkzeug.security import check_password_hash, generate_password_hash

version_regex = r'^\d+(?:\.\d+)+$'
name_regex = r'^[a-z]+(?:-[a-z]+)*$'
zip_regex = r'^[a-z]+(?:-[a-z]+)*\-\d+(?:\.\d+)+\.zip'


def is_valid_filename(filename) -> bool:
    return bool(re.match(zip_regex, filename))


def is_valid_version(version) -> bool:
    return bool(re.match(version_regex, version))


def is_valid_chart_name(name) -> bool:
    return bool(re.match(name_regex, name))


def is_readable_dir(path: str) -> bool:
    return os.path.isdir(path) and os.access(path, os.R_OK)


def to_dicts(arr):
    return [x.to_dict() for x in arr]


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def hash_password(password: str) -> str:
    """
    Create a hash of the password using randomly generated salt.
    """
    return generate_password_hash(password, salt_length=12)


def check_password(password: str, hashed_password: str) -> bool:
    """
    Compare the password against its hashed variant.
    """
    return check_password_hash(hashed_password, password)


def parse_archive_filename(filename):
    """
    Read the filename of the requested archive and return
    both the chart name and the release version.
    """
    chunks = filename[:-4].split('-')
    chart_name = '-'.join(chunks[:-1])
    version = chunks[-1]

    return chart_name, version
