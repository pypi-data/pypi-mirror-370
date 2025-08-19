import json
import uuid
from typing import Optional, List

from pydantic import Field
from pydantic.main import BaseModel

from solax_py_library.device.constant.cabinet import TRENE_CABINET_ENUM
from solax_py_library.smart_scene.types.action import (
    SmartSceneAction,
    ActionType,
    SystemActionType,
)
from solax_py_library.smart_scene.types.base import translator
from solax_py_library.smart_scene.types.condition import (
    RepeatFunc,
    SmartSceneCondition,
    LogicFunc,
    ConditionType,
    PriceConditionType,
    ConditionFunc,
    WeekDay,
)


class SmartSceneOtherInfo(BaseModel):
    duration_times: Optional[int] = Field(
        description="如果需要判断持续时间，记录当前已持续的时间", default=0
    )
    version: Optional[float] = Field(description="记录版本，用于管理", default=9)
    once_flag: Optional[bool] = Field(
        description="是否是单次执行，默认False", default=False
    )

    @classmethod
    def new_other_info(cls, version=None):
        return SmartSceneOtherInfo(
            duration_times=0,
            version=version,
            once_flag=False,
        ).dict()


class SmartSceneContent(BaseModel):
    name: str = Field(description="Scene name", max_length=100)
    repeatFunction: Optional[RepeatFunc] = Field(description="重复规则")
    weekList: Optional[List[int]]
    conditions: SmartSceneCondition = Field(alias="if")
    thenActions: List[SmartSceneAction] = Field(alias="then")
    elseThenActions: Optional[List[SmartSceneAction]] = Field(alias="elseThen")

    def set_copy_name(self):
        self.name = self.name + "-copy"

    def build_smart_scene(self, version):
        return {
            "scene_id": str(uuid.uuid4()),
            "switch": False,
            "content": json.dumps(
                {
                    "name": self.name,
                    "repeatFunction": self.repeatFunction,
                    "weekList": self.weekList,
                    "if": self.conditions.dict(),
                    "then": [item.dict() for item in self.thenActions],
                    "elseThen": [item.dict() for item in self.elseThenActions]
                    if self.elseThenActions
                    else None,
                }
            ),
            "other": json.dumps(SmartSceneOtherInfo.new_other_info(version)),
        }

    @classmethod
    def rec_scene(cls, lang, cabinet_type):
        scene_rec_1 = {
            "name": translator.translate("rec_name_01", lang),
            "instruction": translator.translate("instruction_01", lang),
            "repeatFunction": RepeatFunc.EVERYDAY,
            "weekList": [1, 2, 3, 4, 5, 6, 7],
            "if": {
                "operation": LogicFunc.AND,
                "value": [
                    {
                        "type": ConditionType.buyingPrice,
                        "data": [
                            {
                                "childType": PriceConditionType.price,
                                "childData": {
                                    "function": ConditionFunc.LT,
                                    "data": [0],
                                },
                            }
                        ],
                    }
                ],
            },
            "then": [
                {
                    "type": ActionType.system,
                    "data": [
                        {
                            "childType": SystemActionType.workMode,
                            "childData": {
                                "data": [16, 9, 0, -60, 100],
                            },
                        }
                    ],
                }
            ],
            "elseThen": [],
        }
        scene_rec_2 = {
            "name": translator.translate("rec_name_02", lang),
            "instruction": translator.translate("instruction_02", lang),
            "repeatFunction": RepeatFunc.EVERYDAY,
            "weekList": [1, 2, 3, 4, 5, 6, 7],
            "if": {
                "operation": LogicFunc.AND,
                "value": [
                    {
                        "type": ConditionType.sellingPrice,
                        "data": [
                            {
                                "childType": PriceConditionType.price,
                                "childData": {
                                    "function": ConditionFunc.LT,
                                    "data": [0],
                                },
                            }
                        ],
                    }
                ],
            },
            "then": [
                {
                    "type": ActionType.system,
                    "data": [
                        {
                            "childType": SystemActionType.exportControl,
                            "childData": {
                                "data": [1, 2, 0, 1],
                            },
                        }
                    ],
                }
            ],
            "elseThen": [],
        }
        if cabinet_type in TRENE_CABINET_ENUM:
            return [scene_rec_2]
        else:
            return [scene_rec_1, scene_rec_2]

    def get_weekday_index(self):
        if self.repeatFunction == RepeatFunc.EVERYDAY:
            return [1, 2, 3, 4, 5, 6, 7]
        elif self.repeatFunction == RepeatFunc.WEEKDAY:
            return [1, 2, 3, 4, 5]
        elif self.repeatFunction == RepeatFunc.WEEKEND:
            return [6, 7]
        elif self.repeatFunction == RepeatFunc.CUSTOM:
            return self.weekList

    def get_condition_types(self):
        condition_types = set()
        for v in self.conditions.value:
            condition_types.add(v.type)
        return condition_types

    def repeat_text_info(self, lang):
        if self.repeatFunction != RepeatFunc.CUSTOM:
            return translator.translate(str(self.repeatFunction), lang)
        else:
            return ",".join(
                [translator.translate(str(WeekDay(d)), lang) for d in self.weekList]
            )
