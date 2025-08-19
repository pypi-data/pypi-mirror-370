from collections import defaultdict

from tornado.log import app_log

from solax_py_library.smart_scene.core.condition.base import BaseCondition
from solax_py_library.smart_scene.types.condition import (
    CabinetConditionItemData,
    CabinetConditionType,
    ConditionType,
)
from solax_py_library.smart_scene.types.condition_value import CabinetValue


class CabinetCondition(BaseCondition):
    condition_type = ConditionType.cabinet

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)
        self.value = defaultdict(lambda: CabinetValue)

    def meet_func(self, data: CabinetConditionItemData, ctx):
        if not self.value:
            return False
        cabinet = ctx["cabinet"] or []
        condition_data = data.childData.data
        for cabinet_sn in cabinet:
            cabinet_value = self.value[cabinet_sn]
            if not cabinet_value:
                continue
            if data.childType == CabinetConditionType.cabinetSoc:
                if self.value[cabinet_sn].soc is None:
                    continue
                app_log.info(
                    f"meet_cabinet_soc: {self.value[cabinet_sn].soc}, data_value: {condition_data[0]}"
                )
                if data.childData.function.function()(
                    self.value[cabinet_sn].soc,
                    condition_data[0],
                ):
                    return True
            elif data.childType == CabinetConditionType.cabinetAlarm:
                alarm_type = condition_data[-1]
                for device_type in condition_data[:-1]:
                    alarm_info = cabinet_value.alarm_info(device_type)
                    if not alarm_info:
                        continue
                    app_log.info(
                        f"meet_cabinet_alarm: {alarm_info}, data_value: {alarm_info[alarm_type-1]}"
                    )
                    if alarm_info[alarm_type - 1] is True:
                        return True
        return False
