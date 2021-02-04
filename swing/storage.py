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


class LocalStorage(StorageInterface):
    def __init__(self, basedir):
        self.basedir = basedir

    def get_file_path(self, release_id):
        return f'{self.basedir}/{release_id}.zip'

    def upload(self, release_id, file):
        path = self.get_file_path(release_id)
        if not os.path.isfile(path):
            file.seek(0)
            file.save(path)

    def download(self, release_id):
        path = self.get_file_path(release_id)
        file = open(path, 'rb')
        return file

    def delete(self, release_id):
        path = self.get_file_path(release_id)
        if os.path.isfile(path):
            os.remove(path)


