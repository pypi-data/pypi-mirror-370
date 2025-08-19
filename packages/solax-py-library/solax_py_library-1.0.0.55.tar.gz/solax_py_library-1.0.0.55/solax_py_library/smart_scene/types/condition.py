import operator
from enum import IntEnum, Enum
from typing import Optional, List, Union, Any

from pydantic import validator, BaseModel

from solax_py_library.device.types.alarm import AlarmLevel
from solax_py_library.device.types.device import DeviceType
from solax_py_library.smart_scene.exceptions.smart_scene import SocLimit
from solax_py_library.smart_scene.types.base import translator


class LogicFunc(IntEnum):
    OR = 0
    AND = 1

    def __str__(self):
        return {
            self.OR: "or",
            self.AND: "and",
        }.get(self)


class ConditionFunc(IntEnum):
    GT = 100
    LT = 101
    EQ = 102

    def function(self):
        return {
            ConditionFunc.GT: operator.gt,
            ConditionFunc.LT: operator.lt,
            ConditionFunc.EQ: operator.eq,
        }.get(self)

    def __str__(self):
        return {
            self.GT: "gt",
            self.LT: "lt",
            self.EQ: "eq",
        }.get(self)


class RepeatFunc(IntEnum):
    ONCE = 103
    EVERYDAY = 104
    WEEKDAY = 105
    WEEKEND = 106
    CUSTOM = 107

    def __str__(self):
        return {
            self.ONCE: "once",
            self.EVERYDAY: "everyday",
            self.WEEKDAY: "weekday",
            self.WEEKEND: "weekend",
            self.CUSTOM: "custom",
        }.get(self)


class WeekDay(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    def __str__(self):
        return {
            self.MONDAY: "monday",
            self.TUESDAY: "tuesday",
            self.WEDNESDAY: "wednesday",
            self.THURSDAY: "thursday",
            self.FRIDAY: "friday",
            self.SATURDAY: "saturday",
            self.SUNDAY: "sunday",
        }.get(self)


class ConditionType(str, Enum):
    date = "date"
    weather = "weather"
    buyingPrice = "buyingPrice"
    sellingPrice = "sellingPrice"
    systemCondition = "systemCondition"
    cabinet = "cabinet"


class WeatherConditionType(str, Enum):
    irradiance = "irradiance"
    temperature = "temperature"


class PriceConditionType(str, Enum):
    price = "price"
    lowerPrice = "lowerPrice"
    higherPrice = "higherPrice"
    expensiveHours = "expensiveHours"
    cheapestHours = "cheapestHours"


class DateConditionType(str, Enum):
    time = "time"
    duration = "duration"


class SystemConditionType(str, Enum):
    systemSoc = "systemSoc"
    systemImportPower = "systemImportPower"  # 买电功率
    systemExportPower = "systemExportPower"  # 馈电功率


class CabinetConditionType(str, Enum):
    cabinetAlarm = "cabinetAlarm"
    cabinetSoc = "cabinetSoc"


class SmartSceneUnit(IntEnum):
    PERCENT = 1
    NUM = 2


class ConditionItemChildData(BaseModel):
    function: Optional[ConditionFunc]
    data: List[Any]


class ConditionItemData(BaseModel):
    def check_param(self, ctx):
        ...


class PriceConditionItemData(ConditionItemData):
    childType: PriceConditionType
    childData: ConditionItemChildData

    @validator("childData", always=True)
    def _check_child_data(cls, value, values):
        child_type = values.get("childType")
        if child_type in {
            PriceConditionType.lowerPrice,
            PriceConditionType.higherPrice,
        }:
            assert value.data[0] > 0, ValueError
        elif child_type in {
            PriceConditionType.expensiveHours,
            PriceConditionType.cheapestHours,
        }:
            assert 1 <= value.data[2] <= 24, ValueError
        return value

    def to_text(self, lang, unit):
        data = self.childData.data
        func = self.childData.function
        if self.childType == PriceConditionType.price:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang),
                f"{data[0]:.5f}".rstrip("0").rstrip("."),
                unit,
            )
        elif self.childType in {
            PriceConditionType.lowerPrice,
            PriceConditionType.higherPrice,
        }:
            return translator.translate(self.childType, lang).format(
                f"{data[0]:.5f}".rstrip("0").rstrip("."), "%" if data[1] == 1 else unit
            )
        elif self.childType in {
            PriceConditionType.expensiveHours,
            PriceConditionType.cheapestHours,
        }:
            return translator.translate(self.childType, lang).format(
                data[0], data[1], data[2]
            )


class SystemConditionItemData(ConditionItemData):
    childType: SystemConditionType
    childData: ConditionItemChildData

    @validator("childData", always=True)
    def _check_child_data(cls, value, values):
        child_type = values.get("childType")
        if child_type in {
            SystemConditionType.systemExportPower,
            SystemConditionType.systemImportPower,
        }:
            assert 0 <= value.data[0] <= 100000, ValueError
            value.data[0] = round(value.data[0], 2)  # 功率保留两位小数
        return value

    def to_text(self, lang, unit):
        data = self.childData.data
        func = self.childData.function
        if self.childType == SystemConditionType.systemSoc:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang), data[0]
            )
        elif self.childType in {
            SystemConditionType.systemImportPower,
            SystemConditionType.systemExportPower,
        }:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang), data[0]
            )

    def check_param(self, ctx):
        soc_low_limit = ctx.get("soc_low_limit", 5)
        if self.childType == SystemConditionType.systemSoc:
            soc = self.childData.data[0]
            if soc < soc_low_limit or soc > 100:
                return SocLimit, {"low_limit": soc_low_limit}


class CabinetConditionItemData(ConditionItemData):
    childType: CabinetConditionType
    childData: ConditionItemChildData

    @validator("childData", always=True)
    def _check_child_data(cls, value, values):
        child_type = values.get("childType")
        if child_type == CabinetConditionType.cabinetAlarm:
            assert value.data[-1] in {
                AlarmLevel.TIPS,
                AlarmLevel.NORMAL,
                AlarmLevel.EMERGENCY,
            }, ValueError
        return value

    def to_text(self, lang, unit):
        data = self.childData.data
        func = self.childData.function
        if self.childType == CabinetConditionType.cabinetSoc:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang), data[0]
            )
        elif self.childType == CabinetConditionType.cabinetAlarm:
            return translator.translate(self.childType, lang).format(
                ",".join(
                    [
                        translator.translate(str(DeviceType(device_type)), lang)
                        for device_type in data[:-1]
                    ]
                ),
                translator.translate(str(AlarmLevel(data[-1])), lang),
            )

    def check_param(self, ctx):
        soc_low_limit = ctx.get("soc_low_limit", 5)
        if self.childType == CabinetConditionType.cabinetSoc:
            soc = self.childData.data[0]
            if soc < soc_low_limit or soc > 100:
                return SocLimit, {"low_limit": soc_low_limit}


class DateConditionItemData(ConditionItemData):
    childType: DateConditionType
    childData: ConditionItemChildData

    @validator("childData", always=True)
    def _check_child_data(cls, value, values):
        child_type = values.get("childType")
        data = value.data
        if child_type == DateConditionType.time:
            assert isinstance(data[0], str), ValueError
        elif child_type == DateConditionType.duration:
            assert isinstance(data[0], int), ValueError
        return value

    def to_text(self, lang, unit):
        if self.childType == DateConditionType.duration:
            return translator.translate(self.childType, lang).format(
                self.childData.data[0]
            )
        elif self.childType == DateConditionType.time:
            return (
                translator.translate(self.childType, lang)
                + "/"
                + self.childData.data[0]
            )


class WeatherConditionItemData(ConditionItemData):
    childType: WeatherConditionType
    childData: ConditionItemChildData

    @validator("childData", always=True)
    def _check_child_data(cls, value, values):
        child_type = values.get("childType")
        if child_type == WeatherConditionType.irradiance:
            assert value.data[0] > 0, ValueError
            assert 0 <= value.data[1] <= 24, ValueError
        return value

    def to_text(self, lang, unit):
        func = self.childData.function
        data = self.childData.data
        if self.childType == WeatherConditionType.irradiance:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang), data[0], data[1]
            )
        else:
            return translator.translate(self.childType, lang).format(
                translator.translate(str(func), lang), data[0]
            )


class ConditionItem(BaseModel):
    type: ConditionType
    cabinet: Optional[List[str]]
    data: List[
        Union[
            DateConditionItemData,
            WeatherConditionItemData,
            PriceConditionItemData,
            SystemConditionItemData,
            CabinetConditionItemData,
        ]
    ]

    @validator("cabinet")
    def _check_cabinet(cls, value, values):
        condition_type = values.get("type")
        if condition_type == ConditionType.cabinet:
            assert value, "cabinet is None"
        return value

    def to_text(self, lang, unit):
        if self.type != ConditionType.cabinet:
            return {self.type: [d.to_text(lang, unit) for d in self.data]}
        elif self.type == ConditionType.cabinet:
            cabinet_sns = ",".join(self.cabinet)
            return {
                self.type: [d.to_text(lang, unit) for d in self.data] + [cabinet_sns]
            }


class SmartSceneCondition(BaseModel):
    operation: LogicFunc
    value: List[ConditionItem]

    def to_text(self, lang, unit):
        ret = {"operation": [translator.translate(str(self.operation), lang)]}
        for v in self.value:
            ret.update(v.to_text(lang, unit))
        return ret

    def get_duration_info(self):
        for item in self.value:
            if item.type != ConditionType.date:
                continue
            for date_item in item.data:
                if date_item.childType == DateConditionType.duration:
                    return (date_item.childData.data[0] // 10) + 1
        return 1
