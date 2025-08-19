from abc import ABCMeta, abstractmethod

from solax_py_library.upload.types.client import UploadData


class BaseUploadService(metaclass=ABCMeta):
    upload_type = None

    def __init__(self, **kwargs) -> None:
        self._client = None
        self._is_connect = False
        self.timeout = 5

    @abstractmethod
    def connect(self):
        ...

    async def upload(self, data: UploadData):
        upload_data = self._parse(data.build_data())
        return self._upload(upload_data)

    @abstractmethod
    def close(self):
        ...

    @property
    def is_connect(self):
        return self._is_connect

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @abstractmethod
    def _upload(self, data):
        ...

    @abstractmethod
    def _parse(self, upload_data: UploadData):
        ...
