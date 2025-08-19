from typing import List, Optional, Dict
from modbus_tk import defines

from pydantic import BaseModel
from enum import IntEnum

from solax_py_library.device.types.modbus_point import ReadModbusPoint, WriteModbusPoint


class InverterModel(IntEnum):
    ...

    def __str__(self):
        ...


class InverterPoint(ReadModbusPoint):
    description: Optional[str]
    point_key: str
    point_id: int
    accuracy: Optional[float]
    function_code: int = defines.READ_INPUT_REGISTERS


class InverterVersionConfig(BaseModel):
    software: ReadModbusPoint
    hardware: ReadModbusPoint


class InverterSystemConfig(BaseModel):
    sn: ReadModbusPoint
    shutdown: WriteModbusPoint
    boot_up: WriteModbusPoint
    time: WriteModbusPoint
    version: InverterVersionConfig


class InverterConfig(BaseModel):
    real_data: List[InverterPoint]
    other_data: InverterSystemConfig
    error_map: Dict[int, int]
