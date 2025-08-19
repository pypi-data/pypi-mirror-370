import copy
import struct
from typing import List

format_map = {
    "int8": {"format_str": "bb", "length": 1},
    "uint8": {"format_str": "BB", "length": 1},
    "int16": {"format_str": "h", "length": 1},
    "uint16": {"format_str": "H", "length": 1},
    "int32": {"format_str": "i", "length": 2},
    "uint32": {"format_str": "I", "length": 2},
    "int64": {"format_str": "q", "length": 4},
    "uint64": {"format_str": "Q", "length": 4},
    "float": {"format_str": "f", "length": 1},
}


def unpack(data: List, data_format, reversed=False):
    """
    :param data: 数据字节, 入参均是由modbus读取到的list[uint16]进行转换
    :param data_format:  数据格式
    :param reversed:  是否翻转大小端
    """
    cur_data = copy.deepcopy(data)
    data_format = data_format.lower()
    if data_format not in format_map:
        raise Exception("暂不支持")
    pack_str = ("<" if reversed else ">") + "H" * len(cur_data)
    to_pack_data = struct.pack(pack_str, *cur_data)
    struct_format = ("<" if reversed else ">") + format_map[data_format]["format_str"]
    return struct.unpack(struct_format, to_pack_data)


def pack(value, fmt, order="big"):
    """将10进制的原始值转换为modbus协议需要的精度与类型的值"""
    opt = "<" if order == "little" else ">"
    if fmt not in format_map:
        raise Exception("暂不支持")
    value = int(value)
    ret = struct.pack(f'{opt}{format_map[fmt]["format_str"]}', value)
    ret_list = struct.unpack(f'{opt}{"H" * format_map[fmt]["length"]}', ret)
    return list(ret_list)
