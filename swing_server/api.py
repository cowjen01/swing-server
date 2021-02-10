from zipfile import ZipFile, BadZipFile

from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden, InternalServerError

from .chart import validate_chart_archive, read_definition
from .config import Config
from .errors import InvalidChartError
from .helpers import to_dicts, is_valid_chart_name, is_valid_version, is_valid_filename, parse_archive_filename
from .models import Chart, Release, db
from .storage import LocalStorage
from .storage import StorageType

main = Blueprint('main', __name__)

if Config.STORAGE_TYPE == StorageType.LOCAL:
    storage = LocalStorage(Config.STORAGE_LOCAL_DIR)


@main.route('/chart', methods=['GET'])
def list_charts():
    """
    Return list of all charts. If the query is specified,
    then filter charts by their name or description.
    """
    query = request.args.get('query')

    chart_query = Chart.query.order_by(Chart.name.asc())

    if query:
        name_filter = (Chart.name.ilike(f'%{query}%') | Chart.description.ilike(f'%{query}%'))
        charts = chart_query.filter(name_filter).all()
    else:
        charts = chart_query.all()

    if not charts:
        return jsonify([])

    response = to_dicts(charts)
    return jsonify(response)


@main.route('/chart/<chart_name>', methods=['DELETE'])
@login_required
def remove_chart(chart_name):
    """
    Remove chart both from the database and from local storage.
    If the version is specified, then remove only the specific release.
    """
    if not is_valid_chart_name(chart_name):
        raise BadRequest(f'Provided name \'{chart_name}\' is not a valid chart name.')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'No chart called \'{chart_name}\' was found.')

    if chart.user_id != current_user.id:
        raise Forbidden('You are not allowed to delete a chart you do not own.')

    version = request.args.get('version')

    if version:
        if not is_valid_version(version):
            raise BadRequest(f'Provided version \'{version}\' is not a valid release version.')

        release = Release.query.filter_by(chart_id=chart.id, version=version).first()

        if not release:
            raise NotFound(f'No release with version \'{version}\' was found.')

        storage.delete(release.id)

        db.session.delete(release)
        db.session.commit()

        return release.to_dict()

    for release in chart.releases:
        storage.delete(release.id)
        db.session.delete(release)

    db.session.delete(chart)
    db.session.commit()

    return chart.to_dict()


@main.route('/release', methods=['POST'])
@login_required
def publish_release():
    """
    Create a new release base on the uploaded archive; validation
    of the archive's content also proceeds. If the chart does not exist,
    then create a new one. If there already is a release with the same version,
    then return an error.
    """
    file = request.files.get('chart')

    if not file or file.filename == '':
        raise BadRequest('The archived chart was not provided.')

    if not is_valid_filename(file.filename.split('/')[-1]):
        raise BadRequest('Provided archive file has not a valid extension.')

    with ZipFile(file, 'r') as zip_file:
        try:
            validate_chart_archive(zip_file)
            definition = read_definition(zip_file)
        except BadZipFile:
            raise BadRequest('Provided file is not a valid ZIP archive.')
        except InvalidChartError as e:
            raise BadRequest(e.message)

    chart = Chart.query.filter_by(name=definition.name).first()

    if chart and chart.user_id != current_user.id:
        raise Forbidden('You are not allowed to publish a release of the chart you do not own.')
    else:
        chart = Chart(
            name=definition.name,
            description=definition.description,
            user_id=current_user.id)

        db.session.add(chart)
        db.session.commit()

    release = Release.query.filter_by(chart_id=chart.id, version=definition.version).first()

    if release:
        raise BadRequest(f'Release with version \'{release.version}\' already exists.')
    else:
        notes = request.form.get('notes')

        release = Release(chart_id=chart.id, version=definition.version, notes=notes)
        chart.description = definition.description

        db.session.add(release)
        db.session.commit()

        storage.upload(release.id, file)

        return release.to_dict()


@main.route('/release', methods=['GET'])
def list_releases():
    """
    Return list of all releases for the specific chart.
    Releases are ordered by the version.
    """
    chart_name = request.args.get('chart')

    if not chart_name:
        raise BadRequest('Chart name has to be provided.')

    if not is_valid_chart_name(chart_name):
        raise BadRequest('Provided name is not a valid chart name.')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'No chart called \'{chart_name}\' was found.')

    release_query = Release.query.order_by(Release.version.desc())
    releases = release_query.filter_by(chart_id=chart.id).all()

    if not releases:
        return jsonify([])

    response = to_dicts(releases)
    return jsonify(response)


@main.route('/release/<filename>', methods=['GET'])
def download_release(filename):
    """
    Download specific release of the chart. The name of the chart
    and version is parsed from the requested filename. The archive
    is sent in the response body as an attachment.
    """
    if not is_valid_filename(filename):
        raise BadRequest('The requested release has not got a valid format.')

    chart_name, version = parse_archive_filename(filename)

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'No chart called \'{chart_name}\' was found.')

    release = Release.query.filter_by(chart_id=chart.id, version=version).first()

    if not release:
        raise NotFound(f'No release with version \'{version}\' was found.')

    file_data = storage.download(release.id)

    if not file_data:
        raise InternalServerError('The release could not be loaded from the server filesystem.')

    file_name = f'{release.get_name()}.zip'

    return send_file(file_data,
                     mimetype='application/zip',
                     as_attachment=True,
                     attachment_filename=file_name)


@main.route('/status', methods=['GET'])
def status():
    """
    Return current server status and a number of created charts.
    Useful when need to check the health of the application.
    """
    charts_total = Chart.query.count()
    return {
        'status': 'ok',
        'charts': charts_total
    }
