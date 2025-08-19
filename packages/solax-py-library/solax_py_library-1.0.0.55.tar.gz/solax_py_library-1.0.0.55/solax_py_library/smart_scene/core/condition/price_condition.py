from datetime import datetime

from tornado.log import app_log

from solax_py_library.smart_scene.core.condition.base import BaseCondition
from solax_py_library.smart_scene.types.condition import (
    PriceConditionItemData,
    PriceConditionType,
    SmartSceneUnit,
    ConditionFunc,
    ConditionType,
)
from solax_py_library.utils.time_util import (
    trans_str_time_to_index,
    get_highest_or_lowest_value,
)


class ElePriceCondition(BaseCondition):
    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)
        self.buy = None

    def meet_func_price(self, function_value: ConditionFunc, data_value, index) -> bool:
        """电价条件的判定"""
        price = self.value["price"]
        if index < 0 or index > len(price):
            return False
        if price[index] is None:
            return False
        app_log.info(f"meet_func_price: {price[index]}, data_value: {data_value[0]}")
        return function_value.function()(price[index], data_value[0])

    def meet_func_highest_price(self, data_value, index) -> bool:
        value, unit = data_value
        price = self.value["price"]
        if None in price[0:96]:
            return False
        max_num = max(price[0:96])
        if unit == SmartSceneUnit.NUM:  # 比最高电价低X元
            base = round(max_num - value, 5)
        else:  # 比最高电价低X%
            if max_num < 0:
                base = round(max_num * (1 + value / 100), 5)
            else:
                base = round(max_num * (1 - value / 100), 5)
        app_log.info(f"meet_func_highest_price: {base}, data_value: {price[index]}")
        if price[index] <= base:
            return True
        else:
            return False

    def meet_func_lowest_price(self, data_value, index) -> bool:
        value, unit = data_value
        price = self.value["price"]
        if None in price[0:96]:
            return False
        min_num = min(price[0:96])
        if unit == SmartSceneUnit.NUM:  # 比最低电价高X元
            base = round(min_num + value, 5)
        else:  # 比最低电价高X%
            if min_num < 0:
                base = round(min_num * (1 - value / 100), 5)
            else:
                base = round(min_num * (1 + value / 100), 5)
        app_log.info(f"meet_func_lowest_price: {base}, data_value: {price[index]}")
        if price[index] >= base:
            return True
        else:
            return False

    def meet_func_highest_or_lowest_hours(self, data_value, index, reverse) -> bool:
        sort_index, start_index = get_highest_or_lowest_value(
            data_value[0],
            data_value[1],
            data_value[2],
            self.value["price"],
            reverse=reverse,
        )
        if sort_index and index - start_index in sort_index:
            return True
        return False

    def meet_func(self, data: PriceConditionItemData, ctx):
        if not self.value or not self.value.get("price"):
            # 未获取到价格数据，直接返回
            return False
        child_data = data.childData
        child_type = data.childType
        data_value = child_data.data
        now_time = datetime.strftime(datetime.now(), "%H:%M")
        index = trans_str_time_to_index(now_time)
        if child_type == PriceConditionType.price:
            return self.meet_func_price(child_data.function, data_value, index)
        elif child_type == PriceConditionType.lowerPrice:
            return self.meet_func_highest_price(data_value, index)
        elif child_type == PriceConditionType.higherPrice:
            return self.meet_func_lowest_price(data_value, index)
        elif child_type == PriceConditionType.expensiveHours:
            return self.meet_func_highest_or_lowest_hours(
                data_value, index, reverse=True
            )
        elif child_type == PriceConditionType.cheapestHours:
            return self.meet_func_highest_or_lowest_hours(
                data_value, index, reverse=False
            )
        return False


class EleSellPriceCondition(ElePriceCondition):
    condition_type = ConditionType.sellingPrice

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)
        self.buy = False


class ElsBuyPriceCondition(ElePriceCondition):
    condition_type = ConditionType.buyingPrice

    def __init__(self, update_value_function, **kwargs):
        super().__init__(update_value_function, **kwargs)
        self.buy = True
