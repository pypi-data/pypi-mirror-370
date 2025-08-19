from tornado.log import app_log

from solax_py_library.smart_scene.core.condition.base import BaseCondition
from solax_py_library.smart_scene.types.condition import (
    DateConditionItemData,
    DateConditionType,
    ConditionType,
)


class DateCondition(BaseCondition):
    condition_type = ConditionType.date

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)

    def meet_func(self, data: DateConditionItemData, ctx):
        if data.childType == DateConditionType.time:
            date = data.childData.data[0]
            hour, minute = date.split(":")
            app_log.info(
                f"meet_time: {self.value.get('hour')}, {self.value.get('minute')}, data_value: {date}"
            )
            if int(hour) == self.value.get("hour") and int(minute) == self.value.get(
                "minute"
            ):
                return True
        return False
