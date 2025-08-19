import os
from enum import IntEnum
from typing import Any, Optional

from pydantic import BaseModel


class FTPFileType(IntEnum):
    CSV = 1

    @classmethod
    def get_file_suffix(cls, value):
        return {
            FTPFileType.CSV: ".csv",
        }.get(value)


class FTPData(BaseModel):
    file_type: FTPFileType
    file_name: str
    data: Any

    def build_full_path(self, remote_path) -> str:
        return os.path.join(remote_path, self.file_name)


class FTPServiceConfig(BaseModel):
    host: str
    port: int
    user: Optional[str]
    password: Optional[str]
    remote_path: str


class FTPParsedData(BaseModel):
    file_name: str
    file_path: str
