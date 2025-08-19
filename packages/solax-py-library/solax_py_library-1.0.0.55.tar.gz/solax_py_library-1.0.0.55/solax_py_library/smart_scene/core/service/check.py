from typing import List, Dict, Any

from solax_py_library.smart_scene.types.action import SmartSceneAction, ActionType
from solax_py_library.smart_scene.types.condition import (
    SmartSceneCondition,
    ConditionType,
)


def action_param_check(actions: List[SmartSceneAction], ctx: Dict[str, Any]):
    """动作里的参数范围判定"""
    for action in actions:
        if action.type != ActionType.system:
            continue
        for action_data in action.data:
            ret = action_data.check_param(ctx)
            if ret is not None:
                return ret
    return True


def condition_param_check(condition: SmartSceneCondition, ctx: Dict[str, Any]):
    for condition_data in condition.value:
        if condition_data.type not in [
            ConditionType.systemCondition,
            ConditionType.cabinet,
        ]:
            continue
        for data in condition_data.data:
            ret = data.check_param(ctx)
            if ret is not None:
                return ret
    return True
