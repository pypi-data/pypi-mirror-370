from tornado.log import app_log

from solax_py_library.smart_scene.core.condition.base import BaseCondition
from solax_py_library.smart_scene.types.condition import (
    SystemConditionItemData,
    SystemConditionType,
    ConditionType,
)


class SystemCondition(BaseCondition):
    condition_type = ConditionType.systemCondition

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)

    def meet_func(self, data: SystemConditionItemData, ctx):
        if not self.value:
            return False
        child_data = data.childData
        function_value = child_data.function
        compare_value = None
        if data.childType == SystemConditionType.systemExportPower:
            compare_value = self.value.get("grid_active_power")
            if compare_value < 0:
                return False
            app_log.info(
                f"meet_system_system_export_power: {compare_value}, data_value: {child_data.data[0]}"
            )
        elif data.childType == SystemConditionType.systemImportPower:
            compare_value = self.value.get("grid_active_power")
            if compare_value > 0:
                return False
            app_log.info(
                f"meet_system_system_import_power: {compare_value}, data_value: {child_data.data[0]}"
            )
        elif data.childType == SystemConditionType.systemSoc:
            compare_value = self.value.get("system_soc")
            app_log.info(
                f"meet_system_soc: {compare_value}, data_value: {child_data.data[0]}"
            )
        if compare_value is None:
            return False
        return function_value.function()(abs(compare_value), child_data.data[0])
