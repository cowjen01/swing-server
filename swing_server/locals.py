
class ErrorMessage:
    CHART_DEFINITION_NAME_EMPTY = 'Chart\'s definition name is empty'
    CHART_DEFINITION_VERSION_EMPTY = 'Chart\'s definition version is empty'
    CHART_DEFINITION_NAME_INVALID = 'Chart\'s definition name is not valid'
    CHART_DEFINITION_VERSION_INVALID = 'Chart\'s definition version is not valid'
    CHART_FILES_DEFINITION_EMPTY = 'Chart\'s definition (chart.yaml) not found'
    CHART_FILES_VALUES_EMPTY = 'Chart\'s default values (values.yaml) not found'
    CHART_FILES_DEPLOYMENT_EMPTY = 'Chart\'s deployment specification (deployment.yaml.j2) not found'
    CHART_FILES_REQUIREMENTS_PRESENT = 'Recursive dependencies (requirements.yaml) are not supported'
