import pytest
import os
from zipfile import ZipFile

from swing_server.chart import *
from helpers import get_fixtures_path


@pytest.mark.parametrize('definition,passed', [
    (ChartDefinition.from_dict({
        'name': 'redis 2',
        'version': '1.0.0',
        'description': 'my redis chart'
    }), False),
    (ChartDefinition.from_dict({
        'name': 'redis-chart',
        'version': '2.3.1'
    }), True),
    (ChartDefinition.from_dict({
        'name': 'postgresql',
        'version': '2.3',
        'description': 'database chart'
    }), True),
    (ChartDefinition.from_dict({
        'name': 'redis-chart',
        'version': 'v2.1'
    }), False),
    (ChartDefinition.from_dict({
        'name': 'psql-chart',
        'version': '2.'
    }), False),
])
def test_validate_definition(definition, passed):
    assert is_definition_valid(definition) == passed


@pytest.mark.parametrize('content,passed', [
    ([
        'configs/s3cmd',
        'chart.yaml',
        'values.yml',
        'deployment.yaml.j2'
    ], True),
    ([
        'chart.yaml',
        'configs/aws'
    ], False),
    ([
        'values.yml',
        'chart',
    ], False),
    ([
        'values.yml',
        'chart.yml',
        'deployment.yml.j2'
    ], True)
])
def test_validate_content(content, passed):
    assert is_content_valid(content) == passed


def test_read_definition():
    chart_path = os.path.join(get_fixtures_path('charts'), 'chart-valid.zip')
    with ZipFile(chart_path) as zip_archive:
        definition = read_definition(zip_archive)

        assert definition.name == 'redis'
        assert definition.version == '1.0.0'


@pytest.mark.parametrize('filename,passed', [
    ('chart-valid.zip', True),
    ('chart-invalid-1.zip', False),
    ('chart-invalid-2.zip', False),
    ('chart-invalid-3.zip', False),
])
def test_validate_chart(filename, passed):
    chart_path = os.path.join(get_fixtures_path('charts'), filename)
    with ZipFile(chart_path) as zip_archive:
        assert is_chart_valid(zip_archive) == passed
