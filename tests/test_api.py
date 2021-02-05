import os
from zipfile import ZipFile

from swing.models import db, Chart, Release, make_user
from structures import ApiTestCase


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CHARTS_PATH = os.path.join(ABS_PATH, 'fixtures', 'charts')


class ApiGeneralTest(ApiTestCase):
    def test_list_charts(self):
        response = self.client.get('/chart')

        self.assert200(response)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0].get('name'), 'redis')
        self.assertEqual(response.json[1].get('name'), 'psql')

    def test_search_charts(self):
        response = self.client.get('/chart', query_string={'query': 'postgres'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('name'), 'psql')

    def test_search_charts_no_result(self):
        response = self.client.get('/chart', query_string={'query': 'foo'})

        self.assert200(response)
        self.assertEqual(len(response.json), 0)

    def test_delete_chart(self):
        self.login('user123@gmail.com', 'pass123')
        response = self.client.delete('/chart/redis')
        chart = Chart.query.filter_by(name='redis').first()

        self.assert200(response)
        self.assertIsNone(chart)

    def test_delete_without_login(self):
        response = self.client.delete('/chart/redis')

        self.assert401(response)

    def test_delete_foreign_chart(self):
        self.login('user456@gmail.com', 'pass456')
        response = self.client.delete('/chart/redis')

        self.assert403(response)

    def test_delete_chart_release(self):
        self.login('user123@gmail.com', 'pass123')
        response = self.client.delete('/chart/redis', query_string={'version': '1.0.0'})
        chart = Chart.query.filter_by(name='redis').first()

        self.assert200(response)
        self.assertEqual(len(chart.releases), 0)

    def test_delete_chart_release_not_found(self):
        self.login('user123@gmail.com', 'pass123')
        response = self.client.delete('/chart/redis', query_string={'version': '3.2.1'})

        self.assert404(response)

    def test_list_releases(self):
        response = self.client.get('/release', query_string={'chart': 'redis'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('version'), '1.0.0')

    def test_list_releases_with_version(self):
        response = self.client.get('/release', query_string={'chart': 'redis', 'version': '1.0'})

        self.assert200(response)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0].get('version'), '1.0.0')

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

    def setUp(self):
        db.create_all()

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
            version='1.0.0'
        )
        db.session.add(release)
        db.session.commit()


class ApiReleaseTest(ApiTestCase):
    def test_a_publish_release(self):
        self.login('user123@gmail.com', 'pass123')

        chart_path = os.path.join(CHARTS_PATH, 'chart-valid.zip')
        with open(chart_path, 'rb') as zip_archive:
            data = dict(
                chart=zip_archive
            )
            response = self.client.post('/release', content_type='multipart/form-data', data=data)
            print(response.json)
            self.assert200(response)
