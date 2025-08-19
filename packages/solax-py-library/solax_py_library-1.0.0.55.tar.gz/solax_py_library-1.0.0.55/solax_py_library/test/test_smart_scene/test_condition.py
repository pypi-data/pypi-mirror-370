from unittest import TestCase

from solax_py_library.device.types.device import DeviceType
from solax_py_library.smart_scene.core.condition import (
    DateCondition,
    BaseCondition,
    CabinetCondition,
)
from solax_py_library.smart_scene.types.condition import (
    CabinetConditionItemData,
    CabinetConditionType,
    ConditionItemChildData,
)
from solax_py_library.smart_scene.types.condition_value import CabinetValue


class TestCondition(TestCase):
    def test_condition_build(self):
        date_condition = DateCondition(
            update_value_function=lambda: 1,
        )
        assert isinstance(date_condition, BaseCondition)

    def test_cabinet_condition_to_text(self):
        cabinet_condition = CabinetConditionItemData(
            childType=CabinetConditionType.cabinetAlarm,
            childData=ConditionItemChildData(
                data=[DeviceType.IO_TYPE, DeviceType.COLD_TYPE, 1]
            ),
        )
        print(cabinet_condition.to_text(lang="zh_CN", unit="嘻嘻"))

    def test_cabinet_condition_check(self):
        cabinet_condition = CabinetCondition(
            update_value_function=lambda: {
                "SN1": CabinetValue(
                    soc=0,
                    io_alarm=[False, True, False],
                ),
            },
        )
        cabinet_condition.update_value()
        assert (
            cabinet_condition.meet_func(
                data=CabinetConditionItemData(
                    childType=CabinetConditionType.cabinetAlarm,
                    childData=ConditionItemChildData(
                        data=[DeviceType.IO_TYPE, DeviceType.COLD_TYPE, 1]
                    ),
                ),
                ctx={"cabinet": ["SN1"]},
            )
            is False
        )
        assert (
            cabinet_condition.meet_func(
                data=CabinetConditionItemData(
                    childType=CabinetConditionType.cabinetAlarm,
                    childData=ConditionItemChildData(
                        data=[DeviceType.IO_TYPE, DeviceType.COLD_TYPE, 2]
                    ),
                ),
                ctx={"cabinet": ["SN1"]},
            )
            is True
        )
