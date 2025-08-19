from typing import Dict


INTERNATIONAL_KEY = [
    "self_use",
    "feedin_priority",
    "back_up_mode",
    "manual_mode",
    "forced_charging",
    "forced_discharging",
    "stop_charging_and_discharging",
    "peak_shaving",
    "vpp",
    "power_control_mode",
    "electric_quantity_target_control_mode",
    "soc_target_control_mode",
    "push_power_positive_negative_mode",
    "push_power_zero_mode",
    "self_consume_charge_discharge_mode",
    "self_consume_charge_only_mode",
    "pv_bat_individual_setting_duration_mode",
    "pv_bat_individual_setting_target_soc_mode",
    "rec_name_01",
    "rec_name_02",
    "instruction_01",
    "instruction_02",
    "gt",
    "lt",
    "eq",
    "or",
    "and",
    "once",
    "everyday",
    "weekday",
    "weekend",
    "date",
    "weather",
    "buyingPrice",
    "sellingPrice",
    "systemCondition",
    "cabinet",
    "irradiance",
    "temperature",
    "price",
    "lowerPrice",
    "higherPrice",
    "expensiveHours",
    "cheapestHours",
    "time",
    "duration",
    "systemSoc",
    "systemImportPower",
    "systemExportPower",
    "cabinetSoc",
    "cabinetAlarm",
    "if",
    "then",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "tips_alarm",
    "normal_alarm",
    "emergency_alarm",
    "pcs",
    "bms",
    "elm",
    "io",
    "air_conditioner",
    "liquid_cooling_unit",
    "environment_monitoring",
    "ess",
    "DoControl",
    "systemSwitch",
    "exportControl",
    "exportControlOff",
    "importControl",
    "importControlOff",
    "importControl_AELIO",
    "importControl_standby",
    "importControl_discharge",
    "workMode",
    "system",
    "on",
    "off",
    "total",
    "per_phase",
    "electricityPrice",
    "or",
    "and",
]


class SmartSceneTranslator:
    _international_map: Dict[str, str] = {key: {} for key in INTERNATIONAL_KEY}

    @classmethod
    def set_internation_map(cls, map_data: Dict[str, str]):
        """Set the internationalization map for the model."""
        cls._international_map = map_data

    @classmethod
    def translate(cls, key: str, lang: str) -> str:
        """Translate a key to the specified language."""
        return cls._international_map.get(key, {}).get(lang, key)


translator = SmartSceneTranslator()
