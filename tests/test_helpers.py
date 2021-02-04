import pytest

from swing.helpers import *

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CHARTS_PATH = os.path.join(ABS_PATH, 'fixtures', 'charts')


@pytest.mark.parametrize('filename,expected', [
    ('chart-redis.zip', True),
    ('chart.zip', True),
    ('readme.md', False)
])
def test_validate_filename(filename, expected):
    assert is_valid_filename(filename) == expected


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
    (CHARTS_PATH, True),
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
