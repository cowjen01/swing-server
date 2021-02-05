from flask_testing import TestCase
from base64 import b64encode

from swing.app import create_app
from swing.auth import create_user
from swing.models import db


class LoginTest(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()

    def post_login(self, credentials):
        return self.client.post('/login', headers={'Authorization': f'Basic {credentials}'})

    def test_login(self):
        credentials = b64encode(b'user123@gmail.com:pass123').decode('utf-8')
        response = self.post_login(credentials)
        self.assert200(response)
        self.assertEqual(response.json.get('email'), 'user123@gmail.com')

    def test_missing_credentials(self):
        response = self.client.post('/login')
        self.assert400(response)

    def test_invalid_header(self):
        credentials = b64encode(b'user123@gmail.com').decode('utf-8')
        response = self.post_login(credentials)
        self.assert400(response)

    def test_invalid_credentials(self):
        credentials = b64encode(b'user123@gmail.com:secret456').decode('utf-8')
        response = self.post_login(credentials)
        self.assert401(response)

    def test_user_not_found(self):
        credentials = b64encode(b'user234@gmail.com:pass123').decode('utf-8')
        response = self.post_login(credentials)
        self.assert404(response)

    def setUp(self):
        db.create_all()
        user = create_user('user123@gmail.com', 'pass123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
