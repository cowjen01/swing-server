import pytest

from swing.helpers import *
from helpers import get_fixtures_path


@pytest.mark.parametrize('filename,expected', [
    ('chart-redis-2.3.zip', True),
    ('chart-1.3.5.zip', True),
    ('readme.md', False),
    ('chart.zip', False),
    ('-1.3.5.zip', False),
])
def test_validate_filename(filename, expected):
    assert is_valid_filename(filename) == expected


@pytest.mark.parametrize('filename,expected', [
    ('chart-redis-2.3.zip', ('chart-redis', '2.3')),
    ('redis-1.3.5.zip', ('redis', '1.3.5')),
])
def test_parse_filename(filename, expected):
    assert parse_filename(filename) == expected


@pytest.mark.parametrize('version,expected', [
    ('1.0.a', False),
    ('2.3', True),
    ('5', False),
    ('1.7.12', True)
])
def test_validate_version(version, expected):
    assert is_valid_version(version) == expected


@pytest.mark.parametrize('name,expected', [
    ('redis', True),
    ('psql-chart', True),
    ('sql db', False),
    ('rasa-12', False)
])
def test_validate_chart_name(name, expected):
    assert is_valid_chart_name(name) == expected


@pytest.mark.parametrize('path,expected', [
    ('foo/path/boo', False),
    (get_fixtures_path('charts'), True),
])
def test_validate_path(path, expected):
    assert is_valid_path(path) == expected


@pytest.mark.parametrize('password', [
    'test123',
    'supersecret'
])
def test_hash_password(password):
    hashed_password = hash_password(password)
    assert check_password(password, hashed_password)
