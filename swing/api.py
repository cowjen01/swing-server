from zipfile import ZipFile, BadZipFile
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden, InternalServerError

from .models import Chart, Release, db
from .helpers import list_to_dict, is_valid_version, is_valid_chart_name, is_valid_filename
from .config import Config
from .storage import StorageType
from .storage import LocalStorage
from .chart import is_chart_valid, read_definition

main = Blueprint('main', __name__)

if Config.STORAGE_TYPE == StorageType.LOCAL:
    storage = LocalStorage(Config.STORAGE_LOCAL_DIR)


@main.route('/chart', methods=['GET'])
def list_charts():
    query = request.args.get('query')

    chart_query = Chart.query.order_by(Chart.name.desc())

    if query:
        name_filter = (Chart.name.ilike(f'%{query}%') | Chart.description.ilike(f'%{query}%'))
        charts = chart_query.filter(name_filter).all()
    else:
        charts = chart_query.all()

    if not charts:
        return jsonify([])

    response = list_to_dict(charts)
    return jsonify(response)


@main.route('/chart/<chart_name>', methods=['DELETE'])
@login_required
def remove_chart(chart_name):
    if not is_valid_chart_name(chart_name):
        raise BadRequest('Invalid chart name')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'Chart {chart_name} not found')

    if chart.user_id != current_user.id:
        raise Forbidden('Forbidden delete operation')

    version = request.args.get('version')

    if version:
        if not is_valid_version(version):
            raise BadRequest('Invalid release version')

        release = Release.query.filter_by(version=version).first()

        if not release:
            raise NotFound(f'Release {version} not found')

        storage.delete(release.id)
        db.session.delete(release)

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

    print(request.files)

    if not file or file.filename == '':
        raise BadRequest('Missing chart archive')

    if not is_valid_filename(file.filename.split('/')[-1]):
        raise BadRequest('Invalid archive file name')

    try:
        zip_file = ZipFile(file, 'r')

        if not is_chart_valid(zip_file):
            zip_file.close()
            raise BadRequest('Invalid chart structure or definition')

        definition = read_definition(zip_file)

        zip_file.close()
    except BadZipFile:
        raise BadRequest('Invalid archive file')

    chart = Chart.query.filter_by(name=definition.name).first()

    if chart:
        if chart.user_id != current_user.id:
            raise Forbidden('Forbidden release operation')
    else:
        chart = Chart(
            name=definition.name,
            description=definition.description,
            user_id=current_user.id)

        db.session.add(chart)
        db.session.commit()

    release = Release.query.filter_by(chart_id=chart.id, version=definition.version).first()

    if release:
        raise BadRequest(f'Release {release.version} already exists')
    else:
        release = Release(chart_id=chart.id, version=definition.version)
        chart.description = definition.description

        db.session.add(release)
        db.session.commit()

        storage.upload(release.id, file)

        return release.to_dict()


@main.route('/release', methods=['GET'])
def list_releases():
    chart_name = request.args.get('chart')

    if not chart_name:
        raise BadRequest('Missing chart name')

    if not is_valid_chart_name(chart_name):
        raise BadRequest('Invalid chart name')

    chart = Chart.query.filter_by(name=chart_name).first()

    if not chart:
        raise NotFound(f'Chart {chart_name} not found')

    version = request.args.get('version')

    if version and not is_valid_version(version):
        raise BadRequest('Invalid release version')

    release_query = Release.query.order_by(Release.version.desc())

    if version:
        version_filter = Release.version.like(f'{version}%')
        releases = release_query.filter(version_filter).all()
    else:
        releases = release_query.all()

    if not releases:
        return jsonify([])

    response = list_to_dict(releases)
    return jsonify(response)


@main.route('/release/<int:release_id>/<filename>', methods=['GET'])
def fetch_release(release_id, filename):
    release = Release.query.get(int(release_id))

    if not release:
        raise NotFound('Release not found')

    file_data = storage.download(release_id)

    if not file_data:
        raise InternalServerError('Download failed')

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
