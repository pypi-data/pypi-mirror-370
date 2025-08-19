from .base import BaseUploadService
from .ftp import FTPUploadService


upload_service_map = {}


def _register(upload_obj):
    upload_service_map[upload_obj.upload_type] = upload_obj


_register(FTPUploadService)


__all__ = ["BaseUploadService", "FTPUploadService"]
