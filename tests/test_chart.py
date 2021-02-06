import pytest
import os
from zipfile import ZipFile

from swing_server.chart import *
from swing_server.errors import InvalidChartError
from helpers import get_fixtures_path


@pytest.mark.parametrize('definition', [
    ChartDefinition.from_dict({
        'name': 'redis-chart',
        'version': '2.3.1'
    }),
    ChartDefinition.from_dict({
        'name': 'postgresql',
        'version': '2.3',
        'description': 'database chart'
    }),
])
def test_valid_definition(definition):
    validate_chart_definition(definition)


@pytest.mark.parametrize('definition', [
    ChartDefinition.from_dict({
        'name': 'redis 2',
        'version': '1.0.0',
        'description': 'my redis chart'
    }),
    ChartDefinition.from_dict({
        'name': 'redis-chart',
        'version': 'v2.1'
    }),
    ChartDefinition.from_dict({
        'name': 'psql-chart',
        'version': '2.'
    }),
])
def test_invalid_definition(definition):
    with pytest.raises(InvalidChartError):
        validate_chart_definition(definition)


@pytest.mark.parametrize('files', [
    [
        'configs/s3cmd',
        'chart.yaml',
        'values.yml',
        'deployment.yaml'
    ],
    [
        'values.yml',
        'chart.yml',
        'deployment.yml'
    ]
])
def test_valid_archive_files(files):
    validate_archive_files(files)


@pytest.mark.parametrize('files', [
    [
        'chart.yaml',
        'configs/aws'
    ],
    [
        'values.yml',
        'chart',
    ],
    [
        'values.yml',
        'chart.yml',
        'deployment.yml',
        'requirements.yaml'
    ]
])
def test_invalid_archive_files(files):
    with pytest.raises(InvalidChartError):
        validate_archive_files(files)


def test_read_definition():
    chart_path = os.path.join(get_fixtures_path('charts'), 'chart-valid.zip')
    with ZipFile(chart_path) as zip_archive:
        definition = read_definition(zip_archive)

        assert definition.name == 'redis'
        assert definition.version == '1.0.0'
        assert definition.description is not None


@pytest.mark.parametrize('filename', [
    'chart-invalid-1.zip',
    'chart-invalid-2.zip',
    'chart-invalid-3.zip',
])
def test_invalid_archive(filename):
    chart_path = os.path.join(get_fixtures_path('charts'), filename)
    with ZipFile(chart_path) as zip_archive:
        with pytest.raises(InvalidChartError):
            validate_chart_archive(zip_archive)
