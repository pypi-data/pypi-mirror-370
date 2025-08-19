import asyncio
import unittest

from solax_py_library.upload.api.service import upload
from solax_py_library.upload.core.upload_service import FTPUploadService
from solax_py_library.upload.exceptions import ConnectError, LoginError
from solax_py_library.upload.types.client import UploadType, UploadData
from solax_py_library.upload.types.ftp import FTPFileType


class FTPTest(unittest.TestCase):
    def test_connect(self):
        ftp_config = {
            "host": "10.1.31.181",  # 测试host
            "port": 21,
            "user": "solax",
            "password": "123456",
            "remote_path": "/xixi",
        }
        ftp = FTPUploadService(**ftp_config)
        ftp.connect()

    def test_connect_error_1(self):
        ftp_config = {
            "host": "10.1.31.182",  # 测试host
            "port": 21,
            "user": "solax",
            "password": "123456",
            "remote_path": "/xixi",
        }
        ftp = FTPUploadService(**ftp_config)
        try:
            ftp.connect()
        except ConnectError:
            ...

    def test_connect_error_2(self):
        ftp_config = {
            "host": "10.1.31.181",  # 测试host
            "port": 21,
            "user": "solax123",
            "password": "123456",
            "remote_path": "/xixi",
        }
        ftp = FTPUploadService(**ftp_config)
        try:
            ftp.connect()
        except LoginError:
            ...

    def test_ftp_upload_to_windows(self):
        ftp_config = {
            "host": "10.1.31.181",  # 测试host
            "port": 21,
            "user": "solax",
            "password": "123456",
            "remote_path": "嘻嘻",
        }
        asyncio.run(
            upload(
                upload_type=UploadType.FTP,
                configuration=ftp_config,
                upload_data=UploadData(
                    upload_type=UploadType.FTP,
                    data=dict(
                        file_type=FTPFileType.CSV,
                        file_name="中文",
                        data=[
                            {
                                "EMS1000序列号": "XMG11A011L",
                                "EMS1000本地时间": "2025-02-11 15:39:10",
                                "EMS1000版本号": "V007.11.1",
                                "电站所在国家和地区": None,
                                "电站所在当前时区": None,
                                "电站系统类型": None,
                            }
                        ],
                    ),
                ),
            )
        )

    def test_ftp_upload_to_linux(self):
        ftp_config = {
            "host": "920729yofx76.vicp.fun",  # 测试host
            "port": 59477,
            "user": "test",
            "password": "test123456",
            "remote_path": "test",
        }
        asyncio.run(
            upload(
                upload_type=UploadType.FTP,
                configuration=ftp_config,
                upload_data=UploadData(
                    upload_type=UploadType.FTP,
                    data=dict(
                        file_type=FTPFileType.CSV,
                        file_name="中文",
                        data=[
                            {
                                "EMS1000序列号": "XMG11A011L",
                                "EMS1000本地时间": "2025-02-11 15:39:10",
                                "EMS1000版本号": "V007.11.1",
                                "电站所在国家和地区": None,
                                "电站所在当前时区": None,
                                "电站系统类型": None,
                            }
                        ],
                    ),
                ),
            )
        )
