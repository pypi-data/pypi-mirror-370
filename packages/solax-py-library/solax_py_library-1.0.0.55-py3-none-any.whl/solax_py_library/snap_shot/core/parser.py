import re
import struct

from solax_py_library.snap_shot.types.address import CommandType
from solax_py_library.snap_shot.constant.crc_table import CRC_Table


class Parser:
    def parse(self, char16):
        """
        :return:
        """
        task_id = self.ascii_to_str(char16[12:76])  # task_id
        device_type = int(char16[76:78])  # 设备类型
        device_sn = self.ascii_to_str(char16[78:118])  # 设备SN
        business_type = int(char16[118:120])
        data = char16[120:]
        return {
            "task_id": task_id,
            "sn": device_sn,
            "device_type": device_type,
            "business_type": business_type,
            "message": char16,
            "data": data,
        }

    def ascii_to_str(self, data: str):
        """阿斯科码转字符串"""
        pattern = re.compile(".{2}")
        message = "\\u00" + "\\u00".join(pattern.findall(data))
        message = message.replace("\\u0000", "")
        message = bytes(message, encoding="utf-8").decode("unicode-escape")
        return message

    def upload_data(self, key: int, big_data: bytes, task_id: str, snap_upload_data):
        business_type = 1  # 1 代表调试信息
        data_type = 0  # 0代表故障录波

        # 分片上传（每包10K）
        chunk_size = 10240
        total_chunks = (len(big_data) + chunk_size - 1) // chunk_size

        # 遍历分片并构造数据包
        for chunk_idx, chunk_data in self.data_chunk_generator(big_data, chunk_size):
            frame = self.build_data_packet_frame(
                task_id=task_id,
                business_type=business_type,
                data_type=data_type,
                total_packets=total_chunks,
                current_packet=key,
                chunk_data=chunk_data,
            )
            snap_upload_data(frame)

    def data_chunk_generator(self, data: bytes, chunk_size: int = 1024):
        """
        将大数据按固定包大小分片
        :param data: 原始数据字节流
        :param chunk_size: 每包最大字节数（默认1024）
        :yield: (当前包序号, 分片数据)
        """
        total = len(data)
        if total == 0:
            yield (0, b"")  # 空数据单独处理
            return

        total_chunks = (total + chunk_size - 1) // chunk_size

        for i in range(total_chunks):
            start = i * chunk_size
            end = start + chunk_size
            yield (i, data[start:end])

    def build_response_frame(
        self, task_id: str, business_type: int, ack_code: int
    ) -> bytes:
        """
        构建接收应答帧（指令类型 0x80）
        :param task_id: 任务ID（32字节）
        :param business_type: 业务类型（0或1）
        :param ack_code: 0-成功，1-失败，2-执行中
        """
        # 固定字段
        header = bytes([0x24, 0x24])
        func_code = bytes([0x05, 0x07])  # 主功能码5 + 子功能码7

        # 数据域
        task_bytes = task_id.encode("ascii")[:32].ljust(32, b"\x00")
        business_byte = bytes([business_type])
        cmd_byte = bytes([CommandType.ACK.value])
        ack_byte = bytes([ack_code])
        data_part = task_bytes + business_byte + cmd_byte + ack_byte

        # 计算长度（功能码2字节 + 数据域37字节 + CRC2字节 = 41）
        frame_length = len(func_code) + len(data_part) + 2
        length_bytes = struct.pack("<H", frame_length)

        # 构建临时帧并计算CRC
        temp_frame = header + length_bytes + func_code + data_part
        crc = self.crc(temp_frame.hex()).upper()
        full_frame = temp_frame + bytes.fromhex(crc)
        return full_frame

    def build_response_all_pack_number(
        self, task_id: str, business_type: int, total_packets: int
    ) -> bytes:
        """
        回复上传总报数
        :param task_id: 任务ID（32字节）
        :param business_type: 业务类型1
        :param total_packets: 总书记包数
        """
        # 固定字段
        header = bytes([0x24, 0x24])
        func_code = bytes([0x05, 0x07])  # 主功能码5 + 子功能码7

        # 数据域
        task_bytes = task_id.encode("ascii")[:32].ljust(32, b"\x00")
        business_byte = bytes([business_type])
        cmd_byte = bytes([CommandType.TOTAL_PACKETS.value])
        data_length = struct.pack("<H", 3)
        data_type_byte = bytes([7])  # 和云平台约定故障录波就传7
        total_packets_bytes = struct.pack("<H", total_packets)
        data_part = (
            task_bytes
            + business_byte
            + cmd_byte
            + data_length
            + data_type_byte
            + total_packets_bytes
        )

        frame_length = len(func_code) + len(data_part) + 2
        length_bytes = struct.pack("<H", frame_length)

        # 构建临时帧并计算CRC
        temp_frame = header + length_bytes + func_code + data_part
        crc = self.crc(temp_frame.hex()).upper()
        full_frame = temp_frame + bytes.fromhex(crc)
        return full_frame

    def build_total_packets_frame(
        self, task_id: str, business_type: int, data_type: int, total_packets: int
    ) -> bytes:
        """
        构建上报总包数帧（指令类型 0x81）
        :param total_packets: 总包数（若为0，平台停止接收）
        """
        header = bytes([0x24, 0x24])
        func_code = bytes([0x05, 0x07])

        # 数据域
        task_bytes = task_id.encode("ascii")[:32].ljust(32, b"\x00")
        business_byte = bytes([business_type])
        cmd_byte = bytes([CommandType.TOTAL_PACKETS.value])
        data_length = struct.pack("<H", 2)  # 数据长度固定2字节
        data_type_byte = bytes([data_type])
        total_packets_bytes = struct.pack("<H", total_packets)

        data_part = (
            task_bytes
            + business_byte
            + cmd_byte
            + data_length
            + data_type_byte
            + total_packets_bytes
        )

        # 计算长度
        frame_length = len(func_code) + len(data_part) + 2
        length_bytes = struct.pack("<H", frame_length)

        # 附加CRC
        temp_frame = header + length_bytes + func_code + data_part
        crc = self.crc(temp_frame.hex()).upper()
        return temp_frame + bytes.fromhex(crc)

    def build_data_packet_frame(
        self,
        task_id: str,
        business_type: int,
        data_type: int,
        total_packets: int,
        current_packet: int,
        chunk_data: bytes,
    ) -> bytes:
        """
        构建具体分包数据帧（指令类型 0x82）
        """
        header = bytes([0x24, 0x24])
        func_code = bytes([0x05, 0x07])

        # 数据域
        task_bytes = task_id.encode("ascii")[:32].ljust(32, b"\x00")
        business_byte = bytes([business_type])
        cmd_byte = bytes([CommandType.DATA_PACKET.value])
        data_type_byte = bytes([data_type])
        total_packets_bytes = struct.pack("<H", total_packets)
        current_packet_bytes = struct.pack("<H", current_packet)
        data_length = struct.pack("<H", len(chunk_data))

        data_part = (
            task_bytes
            + business_byte
            + cmd_byte
            + data_type_byte
            + total_packets_bytes
            + current_packet_bytes
            + data_length
            + chunk_data
        )

        # 计算长度
        frame_length = len(func_code) + len(data_part) + 2
        length_bytes = struct.pack("<H", frame_length)

        # 附加CRC
        temp_frame = header + length_bytes + func_code + data_part
        crc = self.crc(temp_frame.hex()).upper()
        return temp_frame + bytes.fromhex(crc)

    def build_error_frame(
        self, task_id: str, business_type: int, error_type: int
    ) -> bytes:
        """
        构建报错应答帧（指令类型 0x83）

        """
        header = bytes([0x24, 0x24])
        func_code = bytes([0x05, 0x07])

        # 数据域
        task_bytes = task_id.encode("ascii")[:32].ljust(32, b"\x00")
        business_byte = bytes([business_type])
        cmd_byte = bytes([CommandType.ERROR.value])
        error_byte = bytes([error_type])
        data_part = task_bytes + business_byte + cmd_byte + error_byte

        # 计算长度
        frame_length = len(func_code) + len(data_part) + 2
        length_bytes = struct.pack("<H", frame_length)

        # 附加CRC
        temp_frame = header + length_bytes + func_code + data_part
        crc = self.crc(temp_frame.hex()).upper()
        return temp_frame + bytes.fromhex(crc)

    def crc(self, message):
        """获取校验位, message: 除去校验位"""
        crc = 0
        i = 0
        length = len(message) // 2
        while length > 0:
            crc &= 0xFFFFFFFF
            da = crc // 256
            da &= 0xFF
            crc <<= 8
            crc ^= CRC_Table[da ^ int(message[i : i + 2], 16)]
            i += 2
            length -= 1
        return f"{crc & 0xffff:04x}"
