from flask_testing import TestCase
from base64 import b64encode

from swing.app import create_app
from swing.models import db, make_user


class ApiTestCase(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()

    def login(self, email, password=None):
        if email and password:
            credentials_str = f'{email}:{password}'
        else:
            credentials_str = f'{email}'

        credentials = b64encode(bytes(credentials_str, encoding='utf-8')).decode('utf-8')
        return self.client.post('/login', headers={'Authorization': f'Basic {credentials}'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        db.create_all()

        user = make_user('user123@gmail.com', 'pass123')

        db.session.add(user)
        db.session.commit()
