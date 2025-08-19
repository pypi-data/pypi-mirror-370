from solax_py_library.exception import SolaxBaseError


class MissParam(SolaxBaseError):
    code = 0x2001
    message = "smart_scene__miss_param"


class OnlyPositive(MissParam):
    message = "smart_scene__only_positive"


class TimeRange(MissParam):
    message = "smart_scene__time_range"


class IrradianceOnlyPositive(MissParam):
    message = "smart_scene__irradiance_only_positive"


class ExportLimitNum(MissParam):
    message = "smart_scene__export_limit_num"


class ExportLimitPercent(MissParam):
    message = "smart_scene__export_limit_percent"


class ImportLimitNum(MissParam):
    message = "smart_scene__import_limit_num"


class ImportOnlyPositive(MissParam):
    message = "smart_scene__import_only_positive"


class SocLimit(MissParam):
    message = "smart_scene__soc_limit"


class ActivePowerLimitNum(MissParam):
    message = "smart_scene__active_power_limit_num"


class ReactivePowerLimitNum(MissParam):
    message = "smart_scene__reactive_power_limit_num"


class EnergyLimit(MissParam):
    message = "smart_scene__energy_limit"


class PowerLimitNum(MissParam):
    message = "smart_scene__power_limit_num"


class BatteryPowerLimitNum(MissParam):
    message = "smart_scene__battery_power_limit_num"


class PvOnlyGe0(MissParam):
    message = "smart_scene__pv_only_ge_0"


class CountLimit(MissParam):
    message = "smart_scene__count_limit"


class NameLengthLimit(MissParam):
    message = "smart_scene__name_length_limit"


class UniqueLimit(MissParam):
    message = "smart_scene__unique_limit"


class ElectricityPriceFailure(MissParam):
    message = "cloud__electricity_price_failure"


class WeatherFailure(MissParam):
    message = "cloud__weather_failure"
