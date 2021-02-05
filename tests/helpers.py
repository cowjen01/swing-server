import io
import os
import unittest
from zipfile import ZipFile, ZipInfo
from base64 import b64encode

from swing.app import create_app
from swing.models import db, make_user


class ApiTestCase(unittest.TestCase):
    app = None
    client = None

    def login(self, email, password=None):
        if email and password:
            credentials_str = f'{email}:{password}'
        else:
            credentials_str = f'{email}'

        credentials = b64encode(bytes(credentials_str, encoding='utf-8')).decode('utf-8')
        return self.client.post('/login', headers={'Authorization': f'Basic {credentials}'})

    def logout(self):
        return self.client.post('/logout')

    @classmethod
    def setup_app(cls):
        cls.app = create_app()
        cls.app.testing = True
        cls.client = cls.app.test_client()

    @classmethod
    def setup_user(cls):
        with cls.app.app_context():
            user = make_user('user123@gmail.com', 'pass123')
            db.session.add(user)
            db.session.commit()

    @classmethod
    def setUpClass(cls):
        cls.setup_app()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def assert200(self, response):
        self.assertEqual(response.status_code, 200)

    def assert400(self, response):
        self.assertEqual(response.status_code, 400)

    def assert401(self, response):
        self.assertEqual(response.status_code, 401)

    def assert403(self, response):
        self.assertEqual(response.status_code, 403)

    def assert404(self, response):
        self.assertEqual(response.status_code, 404)


def create_test_zip():
    archive = io.BytesIO()
    with ZipFile(archive, 'w') as zip_archive:
        file = ZipInfo('chart.yaml')
        zip_archive.writestr(file, b'name: redis')
    return archive


def get_fixtures_path(folder=''):
    abs_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(abs_path, 'fixtures', folder)
