import unittest
from werkzeug.datastructures import FileStorage

from swing_server.storage import LocalStorage
from helpers import create_test_zip, get_fixtures_path


class StorgeTestCase(unittest.TestCase):
    storage = None
    release_id = 15

    @classmethod
    def setUpClass(cls):
        cls.storage = LocalStorage(get_fixtures_path('charts'))

    def test_a_nofile(self):
        file = self.storage.download(self.release_id)
        self.assertIsNone(file)

    def test_b_upload(self):
        archive = create_test_zip()

        file = FileStorage(archive, filename='redis.zip')
        self.storage.upload(self.release_id, file)
        self.assertTrue(self.storage.file_exists(self.release_id))

        archive.close()

    def test_c_download(self):
        file = self.storage.download(self.release_id)
        self.assertIsNotNone(file)
        self.assertTrue(file.readable())

    def test_d_delete(self):
        self.storage.delete(self.release_id)
        self.assertFalse(self.storage.file_exists(self.release_id))
