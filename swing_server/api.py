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
    if not is_valid_chart_name(chart_name):
        raise BadRequest(f'The provided chart\'s name \'{chart_name}\' is not valid.')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'The chart with the name \'{chart_name}\' doesn\'t exist.')

    if chart.user_id != current_user.id:
        raise Forbidden('You can\'t delete the chart you don\'t own.')

    version = request.args.get('version')

    if version:
        if not is_valid_version(version):
            raise BadRequest(f'The release\'s version \'{version}\' is not valid.')

        release = Release.query.filter_by(chart_id=chart.id, version=version).first()

        if not release:
            raise NotFound(f'The release with the version \'{version}\' doesn\'t exist.')

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
def create_release():
    file = request.files.get('chart')

    if not file or file.filename == '':
        raise BadRequest('You have to provide archived chart in the request.')

    if not is_valid_filename(file.filename.split('/')[-1]):
        raise BadRequest('The file has got invalid file extenstion.')

    with ZipFile(file, 'r') as zip_file:
        try:
            validate_chart_archive(zip_file)
            definition = read_definition(zip_file)
        except BadZipFile:
            raise BadRequest('The file is not valid ZIP archive.')
        except InvalidChartError as e:
            raise BadRequest(e.message)

    chart = Chart.query.filter_by(name=definition.name).first()

    if chart:
        if chart.user_id != current_user.id:
            raise Forbidden('You can\'t upload a release of the chart you don\'t own.')
    else:
        chart = Chart(
            name=definition.name,
            description=definition.description,
            user_id=current_user.id)

        db.session.add(chart)
        db.session.commit()

    release = Release.query.filter_by(chart_id=chart.id, version=definition.version).first()

    if release:
        raise BadRequest(f'The release with the version \'{release.version}\' already exists.')
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
    chart_name = request.args.get('chart')

    if not chart_name:
        raise BadRequest('You have to provide the chart\'s name.')

    if not is_valid_chart_name(chart_name):
        raise BadRequest('The provided chart name \'{chart_name}\' is not valid.')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'The chart with the name \'{chart_name}\' doesn\'t exist.')

    release_query = Release.query.order_by(Release.version.desc())
    releases = release_query.filter_by(chart_id=chart.id).all()

    if not releases:
        return jsonify([])

    response = to_dicts(releases)
    return jsonify(response)


@main.route('/release/<filename>', methods=['GET'])
def fetch_release(filename):
    if not is_valid_filename(filename):
        raise BadRequest('The requested archive filename is not valid.')

    chart_name, version = parse_archive_filename(filename)

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'The chart with the name \'{chart_name}\' doesn\'t exist.')

    release = Release.query.filter_by(chart_id=chart.id, version=version).first()

    if not release:
        raise NotFound(f'The release with the version \'{version}\' doesn\'t exist.')

    file_data = storage.download(release.id)

    if not file_data:
        raise InternalServerError('The requested archive file is not found.')

    file_name = f'{release.get_name()}.zip'

    return send_file(file_data,
                     mimetype='application/zip',
                     as_attachment=True,
                     attachment_filename=file_name)


@main.route('/status', methods=['GET'])
def status():
    charts_total = Chart.query.count()
    return {
        'status': 'ok',
        'charts': charts_total
    }
