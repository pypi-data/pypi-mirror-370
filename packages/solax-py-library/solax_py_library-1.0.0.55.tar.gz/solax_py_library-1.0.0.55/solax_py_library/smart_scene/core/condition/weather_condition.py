from tornado.log import app_log

from solax_py_library.smart_scene.core.condition.base import BaseCondition
from solax_py_library.smart_scene.types.condition import (
    WeatherConditionItemData,
    WeatherConditionType,
    ConditionType,
)
from solax_py_library.utils.time_util import get_rounded_times


class WeatherCondition(BaseCondition):
    condition_type = ConditionType.weather

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)

    def meet_func(self, data: WeatherConditionItemData, ctx):
        if not self.value:
            return False
        child_data = data.childData
        child_type = data.childType
        function_value = child_data.function
        data_value = child_data.data
        nearest_time, right_time = get_rounded_times()
        if (
            nearest_time not in self.value["timeList"]
            and right_time not in self.value["timeList"]
        ):
            return False
        time_now = (
            right_time if nearest_time not in self.value["timeList"] else nearest_time
        )
        index = self.value["timeList"].index(time_now)
        if child_type == WeatherConditionType.irradiance:
            return self.meet_func_irradiance(function_value, data_value, index)
        elif child_type == WeatherConditionType.temperature:
            app_log.info(
                f"meet_temperature: {self.value[child_type]['valueList'][index]}, data_value: {data_value[0]}"
            )
            return function_value.function()(
                self.value[child_type]["valueList"][index],
                data_value[0],
            )
        return False

    def meet_func_irradiance(self, function_value, data_value, index):
        """太阳辐照度判断"""
        irradiance = data_value[0]
        duration = data_value[1]
        meet_num = 0
        meet_flag = False
        if duration == 0:
            meet_flag = True
        elif duration > 24:
            pass
        else:
            # 1. 保证累计duration个小时大于200,
            for value in self.value["irradiance"]["valueList"]:
                if value > 200:
                    meet_num += 1
                    if meet_num >= duration * 4:
                        meet_flag = True
                        break
        if not meet_flag:
            return False
        # 2. 再判断当前太阳辐照度
        app_log.info(
            f"meet_irradiance: {self.value['irradiance']['valueList'][index]}, data_value: {irradiance}"
        )
        return function_value.function()(
            self.value["irradiance"]["valueList"][index], irradiance
        )
