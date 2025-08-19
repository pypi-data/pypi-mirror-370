from .base import InverterProtocol


inverter_protocol_map = {}


def register_protocol(protocol_class: InverterProtocol):
    if protocol_class.inverter_model is None:
        raise RuntimeError("未找到对应的设备类型")
    inverter_protocol_map[protocol_class.inverter_model] = protocol_class


def ProtocolFactory(inverter_model: int, *args, **kwargs) -> InverterProtocol:
    """
    创建协议实例。
    inverter_model: 逆变器类型
    device_info: 设备信息。
    data: 数据。
    """
    protocol_class = inverter_protocol_map.get(inverter_model)
    if not protocol_class:
        raise ValueError(f"未找到名为 '{str(inverter_model)}' 的协议")
    return protocol_class(*args, **kwargs)


def match_pcs(operate_queue, slave_num):
    for device_model in inverter_protocol_map.keys():
        client = ProtocolFactory(device_model)
        sn_data = client.read_sn(operate_queue.modbus_rtu, slave_num)
        if not sn_data:
            continue
        sn = get_char(sn_data)
        inverter_model, _ = client.parse_sn(sn)
        if inverter_model:
            return inverter_model, sn
    return None, None
