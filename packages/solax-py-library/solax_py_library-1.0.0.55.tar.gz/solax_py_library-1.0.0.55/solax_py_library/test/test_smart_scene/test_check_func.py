from unittest import TestCase

from solax_py_library.smart_scene.core.service.check import (
    condition_param_check,
    action_param_check,
)
from solax_py_library.smart_scene.types.action import (
    SmartSceneAction,
    ActionType,
    SystemActionType,
    SystemActionItemData,
    SystemActionChildData,
)
from solax_py_library.smart_scene.types.condition import (
    SmartSceneCondition,
    ConditionItem,
    ConditionType,
    SystemConditionItemData,
    LogicFunc,
    SystemConditionType,
    ConditionItemChildData,
    CabinetConditionItemData,
    CabinetConditionType,
    ConditionFunc,
)


class TestCheckFunc(TestCase):
    def test_check_condition_func(self):
        con = SmartSceneCondition(
            operation=LogicFunc.AND,
            value=[
                ConditionItem(
                    type=ConditionType.systemCondition,
                    data=[
                        SystemConditionItemData(
                            childType=SystemConditionType.systemSoc,
                            childData=ConditionItemChildData(
                                data=[101], function=ConditionFunc.EQ
                            ),
                        ),
                    ],
                    cabinet=None,
                ),
                ConditionItem(
                    type=ConditionType.cabinet,
                    data=[
                        CabinetConditionItemData(
                            childType=CabinetConditionType.cabinetSoc,
                            childData=ConditionItemChildData(
                                data=[4], function=ConditionFunc.EQ
                            ),
                        )
                    ],
                    cabinet=["1", "2"],
                ),
            ],
        )
        ret = condition_param_check(con, ctx={"soc_low_limit": 10})
        assert ret is not None

    def test_check_action_func(self):
        action = [
            SmartSceneAction(
                type=ActionType.system,
                data=[
                    SystemActionItemData(
                        childType=SystemActionType.importControl,
                        childData=SystemActionChildData(data=[1, -10]),
                    )
                ],
            )
        ]
        ret = action_param_check(
            actions=action,
            ctx={
                "cabinet_type": 3,
                "total_power": 1,
                "total_power_except_solar_inv": 1,
                "total_energy": 1,
            },
        )
        assert ret is not None
