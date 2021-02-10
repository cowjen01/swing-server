import os
from abc import ABC, abstractmethod


class StorageType:
    LOCAL = 'local'


class StorageInterface(ABC):
    """
    Interface for creating different types of storage for the archived
    charts. Every storage has to implement at least four methods for uploading,
    downloading, deleting, and checking the existence of the archives.
    """
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
        """
        Get the ID of the release and return the path to the archive.
        """
        return f'{self.basedir}/{release_id}.zip'

    def upload(self, release_id, file):
        """
        If there is not any release with the same ID, then store
        the archive in the filesystem.
        """
        if not self.file_exists(release_id):
            path = self.get_file_path(release_id)
            file.seek(0)
            file.save(path)

    def download(self, release_id):
        """
        Load archive from the filesystem using release ID.
        """
        if self.file_exists(release_id):
            path = self.get_file_path(release_id)
            file = open(path, 'rb')
            return file
        return None

    def delete(self, release_id):
        """
        Delete archive from the filesystem using release ID.
        """
        if self.file_exists(release_id):
            path = self.get_file_path(release_id)
            os.remove(path)

    def file_exists(self, release_id):
        """
        Check if the archive with the release ID is already stored.
        """
        path = self.get_file_path(release_id)
        return os.path.isfile(path)
