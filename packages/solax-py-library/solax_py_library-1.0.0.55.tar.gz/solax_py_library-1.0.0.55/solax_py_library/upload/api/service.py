from typing import Dict, Any

from solax_py_library.upload.core.upload_service import upload_service_map
from solax_py_library.exception import SolaxBaseError
from solax_py_library.upload.types.client import UploadType, UploadData


def upload_service(upload_type: UploadType, configuration: Dict[str, Any]):
    """
    upload_type: 上传类型。
    configuration: 配置信息
    """
    upload_class = upload_service_map.get(upload_type)
    if not upload_class:
        raise SolaxBaseError
    return upload_class(**configuration)


async def upload(
    upload_type: UploadType, configuration: Dict[str, Any], upload_data: UploadData
):
    service = upload_service(upload_type, configuration)
    with service as s:
        await s.upload(upload_data)
