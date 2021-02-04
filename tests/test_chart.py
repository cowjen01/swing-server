import pytest
import os
from zipfile import ZipFile

from swing.chart import *


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CHARTS_PATH = os.path.join(ABS_PATH, 'fixtures', 'charts')


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
def test_definition_validation(definition, passed):
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
def test_content_validation(content, passed):
    assert is_content_valid(content) == passed


@pytest.mark.parametrize('filename,passed', [
    ('chart-valid.zip', True),
    ('chart-invalid-1.zip', False),
    ('chart-invalid-2.zip', False),
    ('chart-invalid-3.zip', False),
])
def test_chart_validation(filename, passed):
    chart_path = os.path.join(CHARTS_PATH, filename)
    with ZipFile(chart_path) as zip_archive:
        assert is_chart_valid(zip_archive) == passed
