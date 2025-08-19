import json
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from datetime import datetime
from typing import List, Union

from pydantic.class_validators import Validator

from solax_py_library.device.types.inverter_config import InverterConfig, InverterPoint
from solax_py_library.device.types.modbus_point import WriteModbusPoint, ReadModbusPoint
from solax_py_library.utils.common import round_value
from solax_py_library.utils.struct_util import unpack


class InverterProtocol(metaclass=ABCMeta):
    inverter_model: None

    def __init__(self, point_config):
        self.col_name_index_map = OrderedDict()
        self.col_index_name_map = OrderedDict()
        self.col_id_index_map = {}
        self.sn_config = None
        self.shutdown_config = None
        self.boot_up_config = None
        self.time_config = None
        self.version_config = None
        self.error_map = None
        self._prepare(point_config)

    def _prepare(self, point_config: str):
        point_config = json.loads(point_config)
        self.real_data_start_address = None
        self.real_data_end_address = None
        try:
            point_config = InverterConfig(**point_config)
        except Validator as e:
            print(e)
        for index, real_point in enumerate(point_config.real_data):
            point_key = real_point.point_key
            point_id = real_point.point_id
            self.col_name_index_map[point_key] = real_point
            self.col_index_name_map[point_id] = real_point
            self.col_id_index_map[point_id] = index
            self.real_data_start_address = min(
                self.real_data_start_address, real_point.starting_address
            )
            self.real_data_end_address = max(
                self.real_data_end_address,
                real_point.starting_address + real_point.quantity_of_x - 1,
            )

        self.sn_config = point_config.other_data.sn
        self.shutdown_config = point_config.other_data.shutdown
        self.boot_up_config = point_config.other_data.boot_up
        self.time_config = point_config.other_data.time
        self.version_config = point_config.other_data.version

        self.error_map = point_config.error_map

    def read_real_data(self, modbus_client, slave):
        real_data = self._execute_modbus(
            modbus_client,
            slave,
            ReadModbusPoint(
                starting_address=self.real_data_start_address,
                quantity_of_x=self.real_data_end_address
                - self.real_data_start_address
                + 1,
                function_code=InverterPoint.function_code,
            ),
        )
        ret_real_data = {}
        for point_id, point_info in self.col_index_name_map.items():
            offset = point_info.starting_address
            data = real_data[offset : offset + point_info.quantity_of_x]
            ret_real_data[point_id] = self._parse_point_data(point_info, data)
        return ret_real_data

    def read_real_data_to_list(self, modbus_client, slave):
        real_data = self.read_real_data(modbus_client, slave)
        return list(real_data.values())

    def _parse_point_data(self, point_info: InverterPoint, point_data):
        value = unpack(
            point_data, data_format=point_info.register_dataformat, reversed=True
        )
        accuracy = point_info.accuracy
        return round_value(value * accuracy, 3)

    def get_data_by_point_id_from_list(self, point_id, real_data):
        point_index = self.col_id_index_map[point_id]
        return real_data[point_index]

    @abstractmethod
    def get_real_power(self, read_data):
        raise NotImplementedError()

    @abstractmethod
    def get_error_data(self, read_data):
        raise NotImplementedError()

    @abstractmethod
    def parse_pcs_status(self, read_data):
        ...

    @abstractmethod
    def parse_error_code(self, error_data):
        ...

    def error_to_alarm_code(self, error_codes: List[int]):
        if not self.error_map:
            return error_codes
        alarm_codes = []
        for error_code in error_codes:
            if alarm_code := self.error_map.get(error_code):
                alarm_codes.append(alarm_code)
        return alarm_codes

    def pv_power_data(self, real_data):
        ...

    def get_pv_capacity(self, real_data, history_data):
        ...

    def get_active_power(self, read_data):
        ...

    def get_reactive_power(self, read_data):
        ...

    # ==============================  read or write =========================================

    def _execute_modbus(
        self,
        modbus_client,
        slave_num,
        point_info: Union[WriteModbusPoint, ReadModbusPoint],
        output_value=None,
    ):
        try:
            ret = modbus_client.read_and_write(
                slave_num,
                **point_info.dict(
                    include={"starting_address", "quantity_of_x", "function_code"}
                ),
                output_value=output_value,
            )
        except Exception as e:
            print(e)
        return ret

    def shutdown(self, modbus_client, slave_num):
        self._execute_modbus(
            modbus_client,
            slave_num,
            self.shutdown_config,
            output_value=self.shutdown_config.output_value,
        )

    def boot_up(self, modbus_client, slave_num):
        self._execute_modbus(
            modbus_client,
            slave_num,
            self.boot_up_config,
            output_value=self.boot_up_config.output_value,
        )

    def read_sn(self, modbus_client, slave_num):
        return self._execute_modbus(modbus_client, slave_num, self.sn_config)

    def read_soft_version_and_hard_version(self, modbus_client, slave_num):
        soft_inv_version = self.read_soft_version(modbus_client, slave_num)
        hard_inv_version = self.read_hard_version(modbus_client, slave_num)
        return soft_inv_version, hard_inv_version

    def read_soft_version(self, modbus_client, slave_num):
        return self._execute_modbus(
            modbus_client, slave_num, self.version_config.software
        )

    def read_hard_version(self, modbus_client, slave_num):
        return self._execute_modbus(
            modbus_client, slave_num, self.version_config.hardware
        )

    def get_upgrade_value(self, crc, file_size):
        crc_nums = [crc[1], crc[0]]
        file_size = [file_size[1], file_size[0]]
        value = (
            [self.inverter_model]
            + crc_nums
            + [1, 0, 0, 0, 0, 0, 0]
            + file_size
            + [1, 0, 0]
        )
        return value

    def write_pcs_time(self, modbus_client, slave_num):
        self._execute_modbus(
            modbus_client,
            slave_num,
            self.time_config,
            output_value=self._build_pcs_time_value(),
        )

    def _build_pcs_time_value(self):
        cur_time = datetime.now()
        return [
            cur_time.year,
            cur_time.month,
            cur_time.day,
            cur_time.hour,
            cur_time.minute,
            cur_time.second,
        ]
