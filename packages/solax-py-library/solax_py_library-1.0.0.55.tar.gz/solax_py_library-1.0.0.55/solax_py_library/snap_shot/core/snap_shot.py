from typing import Dict, Optional, List
import asyncio

from solax_py_library.snap_shot.exceptions import SnapshotTimeoutError

from solax_py_library.snap_shot.core.base_modbus import ModbusClientBase
from solax_py_library.snap_shot.types.address import *
from solax_py_library.utils.common import retry
from .parser import Parser


class SnapshotCore:
    def __init__(self, modbus_client: ModbusClientBase, snap_except=None):
        self.modbus = modbus_client
        self.all_snap_shot_data: Dict[int, List[int]] = {}
        self.snap_except = snap_except

    def __getitem__(self, index: int) -> Optional[List[int]]:
        return self.all_snap_shot_data.get(index)

    async def __aiter__(self):
        for key in self.all_snap_shot_data:
            yield key, self.all_snap_shot_data[key]

    @property
    def all_snap_data(self):
        return self.all_snap_shot_data.copy()

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _set_MCU_source(self):
        print("step 1  设置芯片源")
        result = await self.modbus.write_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_MCUSOURCE.value,
            [SnapshotMCUSource.MCU_SOURCE_MDSP.value],
        )
        print(f"step 1  设置芯片源回复:0x{result[0]:04x}")

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _set_export_device(self):  # 设置输出设备
        print("setp 2  设置导出设备")

        result = await self.modbus.write_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_EXPORTDEVICE.value,
            [SnapshotExportDevice.EXPORT_DEVICE_UART.value],
        )
        print(f"setp 2  设置导出设备：0x{result[0]:04x}")

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_snapshot_total_number(self) -> int:  # 取得快照总数
        print("step 3  获取快照总数")
        try_number = 3
        number = 0
        result = [0]
        while number < try_number:
            result = await self.modbus.read_registers(
                SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_TOTALNUMBER.value, 1
            )
            print(f"step 3  获取快照总数 :{result}")
            if result[0] > 0:
                break
            number += 1
        return result[0]

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _start_snap_shot(self):  # 获取快照开始结果
        print("第4步  录播开始")
        result = False
        readresultcnt = 0
        while readresultcnt < 3:
            result = await self.modbus.write_registers(
                SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_START.value,
                [SnapshotStartResult.SNAPSHOT_START_START.value],
            )
            print(f" 设置录播开始{result}")
            await asyncio.sleep(1)
            response = await self.modbus.read_registers(
                SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_START.value, 1
            )
            print(f"录波读取设置变量:{response}")

            if response[0] == SnapshotStartResult.SNAPSHOT_START_SUCCESS.value:
                print("设置录播开始成功")
                result = True
                break
            else:
                print("设置录播开始失败")
                result = False
                readresultcnt += 1

        return result

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_snapshot_dataPara(
        self
    ):  # 取得快照数据参数  数据总数  通道数  通道数据深度
        print("step 5  获取快照数据参数")
        result = await self.modbus.read_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_DATASIZE.value, 3
        )
        print(f"step 5  获取快照数据参数:{result}")
        return result[0]

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_Single_snap_shot_data(
        self, index: int, DataNumber: int
    ):  # 获取单个快照数据
        readdatanum = 0
        packindex = 0

        await self._set_snap_shot_data_index(index)  # 设置快照索引
        # 把每次录波参数数量 和参数数据点数量假如的头部
        param_number = await self.modbus.read_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_CHANNELNUMBER.value, 2
        )
        self.all_snap_shot_data.setdefault(index, []).extend(param_number)
        while readdatanum < DataNumber:
            if await self._get_data_pack_read_state() is False:  # 获取数据包读取状态
                raise self.snap_except("读取数据包错误")

            siglepackdatanum = DataNumber - readdatanum
            if siglepackdatanum > 256:
                siglepackdatanum = 256
            # print(f"第{index}次快照，第{packindex}包，读取数据个数：{siglepackdatanum}")

            await self._get_data_pack_index()  # 取得数据包索引
            once_data = await self._get_data_pack(
                siglepackdatanum
            )  # 获取快照数据的单个pack
            self.all_snap_shot_data.setdefault(index, []).extend(once_data)

            await (
                self._clear_data_pack_read_state()
            )  # 清除数据包读取状态  让下位机切pack
            readdatanum += siglepackdatanum
            packindex += 1
            # print(f'self.all_snap_shot_data:{self.all_snap_shot_data}')

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)  #
    async def _set_snap_shot_data_index(self, index: int):  # 设置快照数据索引
        print("step 6  设置快照索引")
        result = await self.modbus.write_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_SNAPSHOTINDEX.value,
            [index],
        )
        print(f"step 6 设置快照索引返回值：0x{result[0]:04x}")

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_data_pack_read_state(self):  # 取得数据包就绪状态
        # print(f'取得数据包就绪状态')
        readcnt = 0
        result = False
        # print(f"readcnt:{readcnt}")
        while readcnt < 100:
            result = await self.modbus.read_registers(
                SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_PACKDATASTATUS.value, 1
            )
            status = result[0]
            if status == 1:
                # print(f'数据包就绪状态为：{status}，数据包就绪')
                result = True
                break
            else:
                # print(f'数据包就绪状态为：{status}，数据包未就绪')
                readcnt += 1
                await asyncio.sleep(0.5)
        return result

    @retry(max_attempts=5, delay=0.2)
    async def _get_data_pack_index(self):  # 取得数据包索引
        # print(f'获取数据包索引')
        result = await self.modbus.read_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_PACKINDEX.value, 1
        )
        packnum = result[0]
        # print(f'当前数据包的索引：{packnum}')
        return packnum

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_data_pack(self, register_num: int) -> List:  # 取得快照数据包
        # print(f'取得快照数据包')
        DataPack = []
        if register_num >= 256:
            response = await self.get_data_pack_h_address(64)
            DataPack.extend(response)
            response = await self._get_data_pack_l_address(64)
            DataPack.extend(response)
        elif register_num >= 64 and register_num < 256:
            response = await self.get_data_pack_h_address(64)
            DataPack.extend(response)
            response = await self._get_data_pack_l_address((register_num - 128) // 2)
            DataPack.extend(response)
        else:
            response = await self.get_data_pack_h_address(register_num // 2)
            DataPack.extend(response)

        print(f"获取快照数据包返回值：{DataPack}")
        return DataPack

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def get_data_pack_h_address(
        self, register_num: int
    ) -> List:  # 取得数据包大小
        data = await self.modbus.read_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_PACKDATA.value,
            register_num,
        )
        return data

    @retry(max_attempts=3, delay=0.5, assign_exception=SnapshotTimeoutError)
    async def _get_data_pack_l_address(
        self, register_num: int
    ) -> List:  # 取得数据包大小
        data = await self.modbus.read_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_PACKDATA.value + 64,
            register_num,
        )
        return data

    @retry(max_attempts=5, delay=0.2, assign_exception=SnapshotTimeoutError)
    async def _clear_data_pack_read_state(self):  # 清除数据包读取状态
        # print(f'清除数据包读取状态')
        await self.modbus.write_registers(
            SnapshotRegisterAddress.SNAPSHOT_REGISTERADDRESS_PACKDATASTATUS.value, [0]
        )
        # print(f'清除数据包就绪状态返回值：{response}')

    @classmethod
    async def start(
        cls,
        modbus_client,
        snap_shot_index: int = 0,
        snap_exception=None,
        snap_upload_data=None,
        task_id="",
    ):
        """启动故障录波
        snap_shot_index : 代表第几个故障 如果传0 就默认读取所有故障
        """
        print("start.................................")
        instance = cls(modbus_client, snap_exception)
        try:
            # 第一步 设置快照芯片源
            await instance._set_MCU_source()
            # 第二步 设置导出设备
            await instance._set_export_device()
            # 第三步 获取设备总数
            total_number = await instance._get_snapshot_total_number()
            total_number_message = Parser().build_response_all_pack_number(
                task_id, 1, total_number
            )
            snap_upload_data(total_number_message)
            if total_number < 1:
                return instance.snap_except("无效的故障录波总数")
            # 第四步 开始录波
            await instance._start_snap_shot()
            # 第5步 获取快照数据参数
            total_data_length = await instance._get_snapshot_dataPara()
            # 第六步 读数据
            for index in range(1, total_number + 1):
                await instance._get_Single_snap_shot_data(index, total_data_length)
            # await instance._get_Single_snap_shot_data(1, total_data_length)

            return instance.all_snap_data

        except Exception as e:
            return instance.snap_except(f"故障录波失败:{e}")

    async def __aenter__(self):
        return self
