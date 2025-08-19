from typing import Union, List

from pydantic import BaseModel
from enum import StrEnum


class ModbusPoint(BaseModel):
    starting_address: int
    quantity_of_x: int
    function_code: int


class RegisterDataformat(StrEnum):
    int8 = "int8"
    uint8 = "uint8"
    int16 = "int16"
    uint16 = "uint16"
    int32 = "int32"
    uint32 = "uint32"
    int64 = "int64"
    uint64 = "uint64"
    float = "float"


class ReadModbusPoint(ModbusPoint):
    register_dataformat: RegisterDataformat


class WriteModbusPoint(ModbusPoint):
    output_value: Union[int, List[int], None]
