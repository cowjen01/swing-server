import os

from swing_server.models import db, Chart, Release, make_user
from helpers import get_fixtures_path, ApiTestCase


class ApiGeneralTest(ApiTestCase):
    def test_list_charts(self):
        response = self.client.get('/chart')

        self.assert200(response)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0].get('name'), 'psql')
        self.assertEqual(response.json[1].get('name'), 'redis')

    def test_search_charts(self):
        response = self.client.get('/chart', query_string={'query': 'postgres'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('name'), 'psql')
        self.assertIsNotNone(response.json[0].get('description'))

    def test_search_charts_no_result(self):
        response = self.client.get('/chart', query_string={'query': 'foo'})

        self.assert200(response)
        self.assertEqual(len(response.json), 0)

    def test_delete_without_login(self):
        response = self.client.delete('/chart/redis')

        self.assert401(response)

    def test_delete_foreign_chart(self):
        self.login('user456@gmail.com', 'pass456')
        response = self.client.delete('/chart/redis')

        self.assert403(response)

    def test_delete_chart_release_not_found(self):
        self.login('user123@gmail.com', 'pass123')
        response = self.client.delete('/chart/redis', query_string={'version': '3.2.1'})

        self.assert404(response)

    def test_list_releases(self):
        response = self.client.get('/release', query_string={'chart': 'redis'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('version'), '1.0.0')
        self.assertEqual(response.json[0].get('notes'), 'First release')

    def test_list_releases_empty_chart_name(self):
        response = self.client.get('/release')

        self.assert400(response)

    def test_list_releases_chart_not_found(self):
        response = self.client.get('/release', query_string={'chart': 'nginx'})

        self.assert404(response)

    def test_server_status(self):
        response = self.client.get('/status')

        self.assert200(response)
        self.assertEqual(response.json.get('charts'), 2)

    @classmethod
    def setUpClass(cls):
        cls.setup_app()
        with cls.app.app_context():
            user1 = make_user('user123@gmail.com', 'pass123')
            user2 = make_user('user456@gmail.com', 'pass456')

            db.session.add(user1)
            db.session.add(user2)

            db.session.commit()

            chart1 = Chart(
                name='redis',
                description='Database Redis chart',
                user_id=user1.id)
            db.session.add(chart1)

            chart2 = Chart(
                name='psql',
                description='Database PostgreSQL chart',
                user_id=user1.id)
            db.session.add(chart2)
            db.session.commit()

            release = Release(
                chart_id=chart1.id,
                version='1.0.0',
                notes='First release'
            )
            db.session.add(release)
            db.session.commit()

    def tearDown(self):
        self.logout()


class ApiReleaseTest(ApiTestCase):
    def test_a_publish_release(self):
        self.login('user123@gmail.com', 'pass123')

        chart_path = os.path.join(get_fixtures_path('charts'), 'valid.zip')
        with open(chart_path, 'rb') as zip_archive:
            data = dict(
                chart=(zip_archive, 'redis-1.0.0.zip')
            )
            response = self.client.post('/release', content_type='multipart/form-data', data=data)

            self.assert200(response)
            self.assertEqual(response.json.get('version'), '1.0.0')

    def test_b_list_charts(self):
        response = self.client.get('/chart')

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('name'), 'redis')

    def test_c_list_releases(self):
        response = self.client.get('/release', query_string={'chart': 'redis'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('version'), '1.0.0')
        self.assertIsNotNone(response.json[0].get('releaseDate'))
        self.assertEqual(response.json[0].get('archiveUrl'), 'http://localhost:5000/release/redis-1.0.0.zip')

    def test_d_download_release_invalid(self):
        response = self.client.get(f'/release/redis-2.4.0.zip')

        self.assert404(response)

    def test_e_download_release(self):
        response = self.client.get(f'/release/redis-1.0.0.zip')

        self.assert200(response)
        self.assertIsNotNone(response.data)

    def test_f_delete_release(self):
        response = self.client.delete('/chart/redis', query_string={'version': '1.0.0'})

        self.assert200(response)

    def test_g_list_releases(self):
        response = self.client.get('/release', query_string={'chart': 'redis'})

        self.assert200(response)
        self.assertEqual(len(response.json), 0)

    def test_h_delete_chart(self):
        response = self.client.delete('/chart/redis')

        self.assert200(response)

    def test_i_list_charts(self):
        response = self.client.get('/chart')

        self.assert200(response)
        self.assertEqual(len(response.json), 0)

    @classmethod
    def setUpClass(cls):
        cls.setup_app()
        cls.setup_user()

