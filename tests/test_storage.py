import os
import io
import unittest
from werkzeug.datastructures import FileStorage
from zipfile import ZipFile, ZipInfo

from swing.storage import LocalStorage

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CHARTS_PATH = os.path.join(ABS_PATH, 'uploads')


def create_zip():
    archive = io.BytesIO()
    with ZipFile(archive, 'w') as zip_archive:
        file = ZipInfo('chart.yaml')
        zip_archive.writestr(file, b'name: redis')
    return archive


class StorgeTestCase(unittest.TestCase):
    def setUp(self):
        self.storage = LocalStorage(CHARTS_PATH)
        self.release_id = 15

    def test_a_nofile(self):
        file = self.storage.download(self.release_id)
        self.assertIsNone(file)

    def test_b_upload(self):
        archive = create_zip()

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
