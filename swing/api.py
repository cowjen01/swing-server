from zipfile import ZipFile
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from .models import Chart, Release, db
from .helpers import list_to_dict, is_valid_version, is_valid_chart_name
from .config import Config
from .storage import StorageType
from .storage import LocalStorage
from .chart import is_chart_valid, read_definition

main = Blueprint('main', __name__)

if Config.STORAGE_TYPE == StorageType.LOCAL:
    storage = LocalStorage(Config.STORAGE_LOCAL_DIR)


@main.route('/status', methods=['GET'])
def status():
    charts_total = Chart.query.count()
    return {
        'status': 'ok',
        'charts': charts_total
    }


@main.route('/chart', methods=['GET'])
def list_charts():
    charts = Chart.query.all()
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

    if not file or file.filename == '':
        raise BadRequest('Missing chart archive')

    # TODO: add file type validation
    zip_file = ZipFile(file, 'r')

    if not is_chart_valid(zip_file):
        zip_file.close()
        raise BadRequest('Invalid chart structure or definition')

    definition = read_definition(zip_file)
    zip_file.close()

    chart = Chart.query.filter_by(name=definition.name).first()

    if chart:
        if chart.user_id != current_user.id:
            raise Forbidden('Forbidden release operation')
    else:
        chart = Chart(name=definition.name, description=definition.description, user_id=current_user.id)
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
        releases = release_query.filter(Release.version.like(f'{version}%')).all()
    else:
        releases = release_query.all()

    if not releases:
        raise NotFound('No release found')

    response = list_to_dict(releases)
    return jsonify(response)


@main.route('/release/<int:release_id>/<filename>', methods=['GET'])
def fetch_release(release_id, filename):
    release = Release.query.get(int(release_id))

    if not release:
        raise NotFound('Release not found')

    file_data = storage.download(release_id)
    file_name = f'{release.get_name()}.zip'

    return send_file(file_data, mimetype='application/zip', as_attachment=True, attachment_filename=file_name)

