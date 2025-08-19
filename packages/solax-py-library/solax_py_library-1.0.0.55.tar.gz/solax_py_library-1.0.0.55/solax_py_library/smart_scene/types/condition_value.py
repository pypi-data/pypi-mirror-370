from typing import List

from pydantic import BaseModel, Field

from solax_py_library.device.types.device import DeviceType


class CabinetValue(BaseModel):
    soc: int = None
    cabinet_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    pcs_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    io_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    bms_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    air_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    liquid_alarm: List[bool] = Field(default_factory=lambda: [False, False, False])
    environment_monitoring_alarm: List[bool] = Field(
        default_factory=lambda: [False, False, False]
    )

    def alarm_info(self, device_type):
        if device_type == DeviceType.ESS_TYPE:
            return self.cabinet_alarm
        elif device_type == DeviceType.PCS_TYPE:
            return self.pcs_alarm
        elif device_type == DeviceType.IO_TYPE:
            return self.io_alarm
        elif device_type == DeviceType.BMS_TYPE:
            return self.bms_alarm
        elif device_type == DeviceType.AIRCONDITIONER_TYPE:
            return self.air_alarm
        elif device_type == DeviceType.COLD_TYPE:
            return self.liquid_alarm
        elif device_type == DeviceType.ENVIRONMENT_MONITORING_TYPE:
            return self.environment_monitoring_alarm
        return None
