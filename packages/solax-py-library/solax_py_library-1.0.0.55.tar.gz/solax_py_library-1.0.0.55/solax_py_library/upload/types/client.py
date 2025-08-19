from enum import IntEnum
from pydantic import BaseModel
from typing import Optional, Union

from solax_py_library.upload.types.ftp import FTPData


class UploadType(IntEnum):
    FTP = 1


class UploadData(BaseModel):
    data: Optional[Union[dict, FTPData]]
    upload_type: UploadType

    def build_data(self):
        dict_obj_data = self.data if isinstance(self.data, dict) else self.data.dict()
        if self.upload_type == UploadType.FTP:
            return FTPData(**dict_obj_data)
