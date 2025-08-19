from enum import IntEnum


class WorkMode(IntEnum):
    self_use = 0
    feedin_priority = 1
    back_up_mode = 2
    manual_mode = 3
    peak_shaving = 4
    tou = 5
    vpp = 16

    def __str__(self):
        return {
            self.self_use: "self_use",
            self.feedin_priority: "feedin_priority",
            self.back_up_mode: "back_up_mode",
            self.manual_mode: "manual_mode",
            self.peak_shaving: "peak_shaving",
            self.vpp: "vpp",
        }.get(self)


class ManualMode(IntEnum):
    forced_charging = 3
    forced_discharging = 4
    stop_charging_discharging = 5

    def __str__(self):
        return {
            self.forced_charging: "forced_charging",
            self.forced_discharging: "forced_discharging",
            self.stop_charging_discharging: "stop_charging_and_discharging",
        }.get(self)


class VppMode(IntEnum):
    power_control_mode = 1
    electric_quantity_target_control_mode = 2
    soc_target_control_mode = 3
    push_power_positive_negative_mode = 4
    push_power_zero_mode = 5
    self_consume_charge_discharge_mode = 6
    self_consume_charge_only_mode = 7
    pv_bat_individual_setting_duration_mode = 8
    pv_bat_individual_setting_target_soc_mode = 9

    def __str__(self):
        return {
            self.power_control_mode: "power_control_mode",
            self.electric_quantity_target_control_mode: "electric_quantity_target_control_mode",
            self.soc_target_control_mode: "soc_target_control_mode",
            self.push_power_positive_negative_mode: "push_power_positive_negative_mode",
            self.push_power_zero_mode: "push_power_zero_mode",
            self.self_consume_charge_discharge_mode: "self_consume_charge_discharge_mode",
            self.self_consume_charge_only_mode: "self_consume_charge_only_mode",
            self.pv_bat_individual_setting_duration_mode: "pv_bat_individual_setting_duration_mode",
            self.pv_bat_individual_setting_target_soc_mode: "pv_bat_individual_setting_target_soc_mode",
        }.get(self)
