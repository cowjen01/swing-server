import os
from abc import ABC, abstractmethod


class StorageType:
    LOCAL = 'local'


class StorageInterface(ABC):
    @abstractmethod
    def upload(self, release_id, data):
        pass

    @abstractmethod
    def download(self, release_id):
        pass

    @abstractmethod
    def delete(self, release_id):
        pass

    @abstractmethod
    def file_exists(self, release_id):
        pass


class LocalStorage(StorageInterface):
    def __init__(self, basedir):
        self.basedir = basedir

    def get_file_path(self, release_id):
        return f'{self.basedir}/{release_id}.zip'

    def upload(self, release_id, file):
        if not self.file_exists(release_id):
            path = self.get_file_path(release_id)
            file.seek(0)
            file.save(path)

    def download(self, release_id):
        if self.file_exists(release_id):
            path = self.get_file_path(release_id)
            file = open(path, 'rb')
            return file
        return None

    def delete(self, release_id):
        if self.file_exists(release_id):
            path = self.get_file_path(release_id)
            os.remove(path)

    def file_exists(self, release_id):
        path = self.get_file_path(release_id)
        return os.path.isfile(path)
