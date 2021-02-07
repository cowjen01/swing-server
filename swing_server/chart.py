import yaml

from .errors import InvalidChartError
from .helpers import is_valid_version, is_valid_chart_name
from .locals import ErrorMessage


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
        raise InvalidChartError(ErrorMessage.CHART_DEFINITION_NAME_EMPTY)

    if not definition.version:
        raise InvalidChartError(ErrorMessage.CHART_DEFINITION_VERSION_EMPTY)

    if not is_valid_chart_name(definition.name):
        raise InvalidChartError(ErrorMessage.CHART_DEFINITION_NAME_INVALID)

    if not is_valid_version(definition.version):
        raise InvalidChartError(ErrorMessage.CHART_DEFINITION_VERSION_INVALID)


def validate_archive_files(files):
    if 'chart.yaml' not in files and 'chart.yml' not in files:
        raise InvalidChartError(ErrorMessage.CHART_FILES_DEFINITION_EMPTY)

    if 'values.yaml' not in files and 'values.yml' not in files:
        raise InvalidChartError(ErrorMessage.CHART_FILES_VALUES_EMPTY)

    if 'deployment.yaml' not in files and 'deployment.yml' not in files:
        raise InvalidChartError(ErrorMessage.CHART_FILES_DEPLOYMENT_EMPTY)

    if 'requirements.yaml' in files or 'requirements.yml' in files:
        raise InvalidChartError(ErrorMessage.CHART_FILES_REQUIREMENTS_PRESENT)


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
