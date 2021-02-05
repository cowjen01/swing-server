from flask_testing import TestCase

from swing.app import create_app
from swing.models import db, Chart, Release
from swing.auth import create_user


class ApiTest(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()

    def test_list_charts(self):
        response = self.client.get('/chart')
        self.assert200(response)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0].get('name'), 'redis')
        self.assertEqual(response.json[1].get('name'), 'psql')

    def test_search_chart(self):
        response = self.client.get('/chart', query_string={'query': 'postgres'})
        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('name'), 'psql')

    def test_empty_search_chart(self):
        response = self.client.get('/chart', query_string={'query': 'foo'})
        self.assert200(response)
        self.assertEqual(len(response.json), 0)

    def test_list_releases(self):
        response = self.client.get('/release', query_string={'chart': 'redis'})
        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('version'), '1.0.0')

    def test_list_releases_empty_chart_nem(self):
        response = self.client.get('/release')
        self.assert400(response)

    def test_list_releases_chart_not_found(self):
        response = self.client.get('/release', query_string={'chart': 'nginx'})
        self.assert404(response)

    def test_server_status(self):
        response = self.client.get('/status')
        self.assert200(response)
        self.assertEqual(response.json.get('charts'), 2)

    def setUp(self):
        db.create_all()

        user = create_user('user123@gmail.com', 'pass123')
        db.session.add(user)
        db.session.commit()

        chart1 = Chart(
            name='redis',
            description='Database Redis chart',
            user_id=user.id)
        db.session.add(chart1)

        chart2 = Chart(
            name='psql',
            description='Database PostgreSQL chart',
            user_id=user.id)
        db.session.add(chart2)
        db.session.commit()

        release = Release(
            chart_id=chart1.id,
            version='1.0.0'
        )
        db.session.add(release)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
