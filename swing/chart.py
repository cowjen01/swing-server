import yaml

from .helpers import is_valid_version, is_valid_chart_name


class ChartDefinition:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        self.description = description

    @classmethod
    def from_dict(cls, json):
        return cls(json.get('name'), json.get('version'), json.get('description'))


def is_definition_valid(definition) -> bool:
    if not definition.name or not definition.version:
        return False

    if not is_valid_chart_name(definition.name):
        return False

    if not is_valid_version(definition.version):
        return False

    return True


def is_content_valid(content) -> bool:
    if 'chart.yaml' not in content and 'chart.yml' not in content:
        return False

    if 'values.yaml' not in content and 'values.yml' not in content:
        return False

    if 'deployment.yaml.j2' not in content and 'deployment.yml.j2' not in content:
        return False

    return True


def read_definition(zip_archive) -> ChartDefinition:
    zip_content = zip_archive.namelist()

    if 'chart.yaml' in zip_content:
        chart_yaml = zip_archive.read('chart.yaml')
    else:
        chart_yaml = zip_archive.read('chart.yml')

    definition_dict = yaml.safe_load(chart_yaml)
    definition = ChartDefinition.from_dict(definition_dict)

    return definition


def is_chart_valid(zip_archive) -> bool:
    if not is_content_valid(zip_archive.namelist()):
        return False

    definition = read_definition(zip_archive)

    if not is_definition_valid(definition):
        return False

    return True

