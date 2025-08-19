import ftplib
import os

from .base import BaseUploadService
from solax_py_library.upload.types.client import UploadType
from solax_py_library.upload.core.data_adapter import CSVDataAdapter
from solax_py_library.upload.types.ftp import (
    FTPServiceConfig,
    FTPFileType,
    FTPData,
    FTPParsedData,
)
from solax_py_library.upload.exceptions.upload_error import (
    SendDataError,
    ConnectError,
    LoginError,
    ConfigurationError,
)


class FTPUploadService(BaseUploadService):
    upload_type = UploadType.FTP

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = self._init_config(**kwargs)
        self.host = config.host
        self.port = config.port
        self.user = config.user
        self.password = config.password
        self.remote_path = config.remote_path

    def _init_config(self, **kwargs):
        try:
            return FTPServiceConfig(**kwargs)
        except Exception as e:
            raise ConfigurationError(message=str(e))

    def connect(self):
        if self._client is not None:
            self.close()
        self._connect()
        self._login()
        self._is_connect = True

    def _connect(self):
        try:
            self._client = ftplib.FTP()
            self._client.encoding = "utf8"  # 默认需要配置为utf8
            self._client.connect(self.host, self.port, timeout=self.timeout)
        except Exception as e:
            raise ConnectError(message=str(e))

    def _login(self):
        try:
            self._client.login(self.user, self.password)
        except Exception as e:
            raise LoginError(message=str(e))

    def close(self):
        if self._client:
            self._client.quit()
            self._client = None
            self._is_connect = False
            print("Connection closed.")

    def _parse(self, upload_data: FTPData) -> FTPParsedData:
        if upload_data.file_type == FTPFileType.CSV:
            parsed_data = CSVDataAdapter.parse_data(upload_data.data)
        else:
            raise NotImplementedError
        return FTPParsedData(
            file_name=upload_data.file_name
            + FTPFileType.get_file_suffix(upload_data.file_type),
            file_path=parsed_data,
        )

    def _upload(self, data: FTPParsedData):
        try:
            if not self._is_connect:
                raise ConnectError(message="not connect yet")
            # self._client.set_pasv(False)
            self._cwd_folder()
            with open(data.file_path, "rb") as f:
                self._client.storbinary(f"STOR {data.file_name}", f)
            print(f"Successfully uploaded to {data.file_name}")
        except Exception as e:
            raise SendDataError(message=str(e))
        finally:
            if os.path.exists(data.file_path):
                os.remove(data.file_path)

    def _cwd_folder(self):
        try:
            self._client.cwd(self.remote_path)
        except Exception as e:
            print(f"CWD error: {e}")
            self._client.mkd(self.remote_path)
            self._client.cwd(self.remote_path)
            print(f"mkdir {self.remote_path}, remove successfully")

    def _build_remote_file(self, file_name):
        return os.path.join(self.remote_path, file_name)
