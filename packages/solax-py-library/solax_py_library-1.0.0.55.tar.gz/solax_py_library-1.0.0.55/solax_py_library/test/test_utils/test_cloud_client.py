from unittest import TestCase

from solax_py_library.utils.cloud_client import CloudClient


class TestCloudClient(TestCase):
    def test_get_weather(self):
        client = CloudClient()
        ret = client.get_weather_data_from_cloud(
            "https://aliyun-sit.solaxtech.net:5050",
            "XMG11A011L",
            "b080a22827484db6bd509d496f9df90b",
        )
        print(ret)
