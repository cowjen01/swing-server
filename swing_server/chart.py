import yaml

from .errors import InvalidChartError
from .helpers import is_valid_version, is_valid_chart_name


class ChartDefinition:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    @classmethod
    def from_dict(cls, json):
        return cls(json.get('name'), json.get('version'), json.get('description'))


def validate_chart_definition(definition):
    if not definition.name:
        raise InvalidChartError('The chart\'s name is empty.')

    if not definition.version:
        raise InvalidChartError('The chart\'s version is empty.')

    if not is_valid_chart_name(definition.name):
        raise InvalidChartError('The chart\'s name is not valid.')

    if not is_valid_version(definition.version):
        raise InvalidChartError('The chart\'s version is not valid.')


def validate_archive_files(files):
    if 'chart.yaml' not in files and 'chart.yml' not in files:
        raise InvalidChartError('The chart\'s definition (chart.yaml) is not found.')

    if 'values.yaml' not in files and 'values.yml' not in files:
        raise InvalidChartError('The chart\'s default values (values.yaml) are not found.')

    if 'deployment.yaml' not in files and 'deployment.yml' not in files:
        raise InvalidChartError('The chart\'s deployment specification (deployment.yaml) is not found.')

    if 'requirements.yaml' in files or 'requirements.yml' in files:
        raise InvalidChartError('The recursive dependencies (requirements.yaml) are not supported.')


def read_definition(zip_archive) -> ChartDefinition:
    zip_content = zip_archive.namelist()

    if 'chart.yaml' in zip_content:
        chart_yaml = zip_archive.read('chart.yaml')
    else:
        chart_yaml = zip_archive.read('chart.yml')

    definition_dict = yaml.safe_load(chart_yaml)
    definition = ChartDefinition.from_dict(definition_dict)

    return definition


def validate_chart_archive(zip_archive):
    validate_archive_files(zip_archive.namelist())

    definition = read_definition(zip_archive)
    validate_chart_definition(definition)
