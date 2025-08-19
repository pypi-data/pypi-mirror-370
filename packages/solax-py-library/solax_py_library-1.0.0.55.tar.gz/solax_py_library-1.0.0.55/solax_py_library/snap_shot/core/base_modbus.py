from abc import ABC, abstractmethod
from typing import List


class ModbusClientBase(ABC):
    @abstractmethod
    async def read_registers(self, address: int, quantity_of_x: int) -> List[int]:
        """抽象读取寄存器方法"""
        pass

    @abstractmethod
    async def write_registers(self, address: int, values: List[int]) -> bool:
        """抽象写入寄存器方法"""
        pass
