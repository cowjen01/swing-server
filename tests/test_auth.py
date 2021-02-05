from flask_testing import TestCase
from base64 import b64encode

from swing.app import create_app
from swing.auth import create_user
from swing.models import db


class LoginTest(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()

    def test_login(self):
        credentials = b64encode(b'cowjen01@gmail.com:pass123').decode('utf-8')
        response = self.client.post('/login', headers={'Authorization': f'Basic {credentials}'})
        self.assert200(response)

    def test_missing_credentials(self):
        response = self.client.post('/login')
        self.assert400(response)

    def test_invalid_authorization(self):
        credentials = b64encode(b'cowjen01@gmail.com').decode('utf-8')
        response = self.client.post('/login', headers={'Authorization': f'Basic {credentials}'})
        self.assert400(response)

    def setUp(self):
        db.create_all()
        user = create_user('cowjen01@gmail.com', 'pass123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
