import json
import ssl
import traceback
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter

from solax_py_library.utils.time_util import trans_str_time_to_index
from tornado.log import app_log


class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)


class CloudClient:
    def __init__(self, base_url, ciphers):
        self.base_url = base_url
        self.ciphers = (
            ciphers
            if ciphers
            else "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384"
        )

    def get_context(self):
        context = ssl.create_default_context()
        context.set_ciphers(self.ciphers)
        return context

    def request(self, url, body=None, headers=None):
        # 创建异步请求
        base_headers = {"Content-Type": "application/json"}
        if headers:
            base_headers.update(headers)

        session = requests.Session()
        session.mount("https://", SSLAdapter(ssl_context=self.get_context()))

        response = session.post(url, json=body, headers=headers, timeout=5)
        if response.status_code != 200:
            raise ValueError(f"访问{url}接口失败")
        return json.loads(response.content.decode("utf-8"))

    def get_token(self, ems_sn, sn_secret):
        token_url = self.base_url + "/device/token/getByRegistrationSn"
        try:
            response_data = self.request(
                url=token_url,
                body={
                    "registrationSn": ems_sn,
                    "snSecret": sn_secret,
                },
            )
            app_log.info(f"获取token结果 {response_data}")
            if response_data.get("result"):
                return response_data["result"]
        except Exception as e:
            app_log.info(f"访问token接口失败: {str(e)}")

    def get_weather_data_from_cloud(self, ems_sn, token):
        """获取未来24小时天气数据"""
        try:
            weather_url = self.base_url + "/ess/web/v1/powerStation/station/solcast/get"
            headers = {"token": token, "Content-Type": "application/json"}
            post_dict = {"registerNo": ems_sn, "day": 1}
            response_data = self.request(
                url=weather_url,
                headers=headers,
                body=post_dict,
            )
            if response_data.get("result") is None:
                app_log.info(f"获取天气数据失败 返回数据 {response_data}")
                return False
            weather_info = {
                "timeList": [],
                "irradiance": {"valueList": []},
                "temperature": {"valueList": []},
                "humidity": {"valueList": []},
                "wind": {"valueList": []},
                "barometricPressure": {"valueList": []},
                "rain": {"valueList": []},
            }
            for info in response_data["result"]:
                weather_info["timeList"].append(info["localTime"])
                weather_info["irradiance"]["valueList"].append(float(info["ghi"]))
                weather_info["temperature"]["valueList"].append(float(info["air_temp"]))
                weather_info["humidity"]["valueList"].append(
                    float(info["relative_humidity"])
                )
                weather_info["wind"]["valueList"].append(float(info["wind_speed_10m"]))
                weather_info["barometricPressure"]["valueList"].append(
                    float(info.get("surface_pressure", 0))
                )
                rain = 1 if float(info["precipitation_rate"]) > 2.5 else 0
                weather_info["rain"]["valueList"].append(rain)
            data_length = len(weather_info["irradiance"]["valueList"])
            if weather_info["timeList"] == []:
                weather_info = {}
            else:
                weather_info["irradiance"]["maxValue"] = max(
                    weather_info["irradiance"]["valueList"]
                )
                weather_info["irradiance"]["avgValue"] = round(
                    sum(weather_info["irradiance"]["valueList"]) / data_length, 3
                )
                weather_info["irradiance"]["minValue"] = min(
                    weather_info["irradiance"]["valueList"]
                )

                weather_info["temperature"]["maxValue"] = max(
                    weather_info["temperature"]["valueList"]
                )
                weather_info["temperature"]["avgValue"] = round(
                    sum(weather_info["temperature"]["valueList"]) / data_length, 3
                )
                weather_info["temperature"]["minValue"] = min(
                    weather_info["temperature"]["valueList"]
                )

                weather_info["humidity"]["maxValue"] = max(
                    weather_info["humidity"]["valueList"]
                )
                weather_info["humidity"]["avgValue"] = round(
                    sum(weather_info["humidity"]["valueList"]) / data_length, 3
                )
                weather_info["humidity"]["minValue"] = min(
                    weather_info["humidity"]["valueList"]
                )

                weather_info["wind"]["maxValue"] = max(
                    weather_info["wind"]["valueList"]
                )
                weather_info["wind"]["avgValue"] = round(
                    sum(weather_info["wind"]["valueList"]) / data_length, 3
                )
                weather_info["wind"]["minValue"] = min(
                    weather_info["wind"]["valueList"]
                )

                weather_info["barometricPressure"]["maxValue"] = max(
                    weather_info["barometricPressure"]["valueList"]
                )
                weather_info["barometricPressure"]["avgValue"] = round(
                    sum(weather_info["barometricPressure"]["valueList"]) / data_length,
                    3,
                )
                weather_info["barometricPressure"]["minValue"] = min(
                    weather_info["barometricPressure"]["valueList"]
                )

                weather_info["rain"]["maxValue"] = max(
                    weather_info["rain"]["valueList"]
                )
                weather_info["rain"]["minValue"] = min(
                    weather_info["rain"]["valueList"]
                )
            app_log.info("获取天气数据成功")
            return weather_info
        except Exception:
            app_log.info(f"获取天气数据失败 异常 {traceback.format_exc()}")
            return False

    def get_electrovalence_data_from_cloud(self, ems_sn, token):
        try:
            price_url = self.base_url + "/powerStation/station/getCurrentElectrovalence"
            response_data = self.request(
                url=price_url,
                body={"registerNo": ems_sn},
                headers={"token": token},
            )
            if response_data.get("result") is None:
                app_log.info(f"获取电价数据失败 返回数据 {response_data}")
                return False
            today = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            ele_price_info = {
                "buy": [None] * 192,
                "sell": [None] * 192,
                "date": today,
            }
            ele_price_info["ele_unit"] = response_data["result"]["unit"]
            if ele_price_info["ele_unit"] == "¥":
                rate = 1
                ele_price_info["ele_unit"] = "¥/kWh"
            else:
                rate = 100
                ele_price_info["ele_unit"] = "Cents €/kWh"
            for detail_info in response_data["result"]["list"]:
                start_index = trans_str_time_to_index(detail_info["startTime"])
                end_index = trans_str_time_to_index(detail_info["endTime"])
                # 处理欧分的情况
                if detail_info["buyPrice"] is not None:
                    buy_price = round(detail_info["buyPrice"] * rate, 5)
                else:
                    buy_price = detail_info["buyPrice"]
                if detail_info["salePrice"] is not None:
                    sale_price = round(detail_info["salePrice"] * rate, 5)
                else:
                    sale_price = detail_info["salePrice"]
                ele_price_info["buy"][start_index:end_index] = [buy_price] * (
                    end_index - start_index
                )
                ele_price_info["sell"][start_index:end_index] = [sale_price] * (
                    end_index - start_index
                )
            if response_data["result"].get("tomorrow") is not None:
                for detail_info in response_data["result"]["tomorrow"]:
                    start_index = trans_str_time_to_index(detail_info["startTime"]) + 96
                    end_index = trans_str_time_to_index(detail_info["endTime"]) + 96
                    if detail_info["buyPrice"] is not None:
                        buy_price = round(detail_info["buyPrice"] * rate, 5)
                    else:
                        buy_price = detail_info["buyPrice"]
                    if detail_info["salePrice"] is not None:
                        sale_price = round(detail_info["salePrice"] * rate, 5)
                    else:
                        sale_price = detail_info["salePrice"]
                    ele_price_info["buy"][start_index:end_index] = [buy_price] * (
                        end_index - start_index
                    )
                    ele_price_info["sell"][start_index:end_index] = [sale_price] * (
                        end_index - start_index
                    )
            app_log.info("获取电价数据成功")
            return ele_price_info
        except Exception:
            app_log.info(f"获取电价数据失败 异常 {traceback.format_exc()}")
            return False
