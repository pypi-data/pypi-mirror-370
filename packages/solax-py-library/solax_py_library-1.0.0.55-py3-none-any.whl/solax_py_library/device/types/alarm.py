from enum import IntEnum


class AlarmLevel(IntEnum):
    """紧急告警、一般告警，状态提醒"""

    EMERGENCY = 1
    NORMAL = 2
    TIPS = 3

    def __str__(self):
        return {
            AlarmLevel.TIPS: "tips_alarm",
            AlarmLevel.NORMAL: "normal_alarm",
            AlarmLevel.EMERGENCY: "emergency_alarm",
        }.get(self)
