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
    """
    Make validation of the chart definition file. Check requirement
    fields, which are the name of the chart and version of the release.
    """
    if not definition.name:
        raise InvalidChartError('Chart name can not be empty.')

    if not definition.version:
        raise InvalidChartError('The release version can not be empty.')

    if not is_valid_chart_name(definition.name):
        raise InvalidChartError('Chart name has not a valid format.')

    if not is_valid_version(definition.version):
        raise InvalidChartError('The release version has not a valid format.')


def validate_archive_files(files):
    """
    Make validation of the archive list of files. Required files
    are the definition of the chart, default values for the deployment,
    and the deployment specification.
    """
    if 'chart.yaml' not in files and 'chart.yml' not in files:
        raise InvalidChartError('The archive does not include a chart definition file.')

    if 'values.yaml' not in files and 'values.yml' not in files:
        raise InvalidChartError('The archive does not include a file with default values.')

    if 'deployment.yaml' not in files and 'deployment.yml' not in files:
        raise InvalidChartError('The archive does not include a deployment specification file.')

    if 'requirements.yaml' in files or 'requirements.yml' in files:
        raise InvalidChartError('Recursive requirements are not currently supported.')


def read_definition(zip_archive) -> ChartDefinition:
    """
    Read the definition file from the archived chart.
    """
    zip_content = zip_archive.namelist()

    if 'chart.yaml' in zip_content:
        chart_yaml = zip_archive.read('chart.yaml')
    else:
        chart_yaml = zip_archive.read('chart.yml')

    definition_dict = yaml.safe_load(chart_yaml)
    definition = ChartDefinition.from_dict(definition_dict)

    return definition


def validate_chart_archive(zip_archive):
    """
    Make validation of both the files and the chart definition.
    """
    validate_archive_files(zip_archive.namelist())

    definition = read_definition(zip_archive)
    validate_chart_definition(definition)
