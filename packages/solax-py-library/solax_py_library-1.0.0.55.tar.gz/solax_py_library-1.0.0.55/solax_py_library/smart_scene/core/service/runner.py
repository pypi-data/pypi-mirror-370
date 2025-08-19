import json
import traceback
from datetime import datetime
from typing import List, Set

from solax_py_library.smart_scene.core.condition import BaseCondition
from solax_py_library.smart_scene.types.action import (
    SmartSceneAction,
)
from solax_py_library.smart_scene.types.condition import (
    ConditionType,
    RepeatFunc,
    LogicFunc,
    SmartSceneCondition,
    DateConditionType,
    ConditionItem,
)
from solax_py_library.smart_scene.types.smart_scene_content import (
    SmartSceneContent,
    SmartSceneOtherInfo,
)
from tornado.log import app_log


class SmartSceneRunner:
    def __init__(self, condition_classes, action_classes):
        self.condition_class_map = {}
        self.action_class_map = {}

        for condition_class in condition_classes:
            if not isinstance(condition_class, BaseCondition):
                raise ValueError(
                    f"condition({condition_class}) is not derived from BaseCondition"
                )
            self.condition_class_map[condition_class.condition_type] = condition_class

        for action_class in action_classes:
            self.action_class_map[action_class.action_type] = action_class

    @staticmethod
    def _handle_repeat_info(scene_content: SmartSceneContent, once_flag):
        # once_flag: 是否执行过
        if scene_content.repeatFunction == RepeatFunc.ONCE:
            return False if once_flag else True
        week_list = scene_content.get_weekday_index()
        if datetime.now().weekday() + 1 in week_list:
            return True
        return False

    def smart_scene_handle(self, scene_instance):
        other_info = SmartSceneOtherInfo.parse_raw(scene_instance.other)
        try:
            scene_data = SmartSceneContent.parse_raw(scene_instance.content)

            # repeat，是否执行
            if not self._handle_repeat_info(scene_data, other_info.once_flag):
                app_log.info(
                    f"场景名称: {scene_data.name}, 场景ID: {scene_instance.scene_id} 不符合重复条件，不执行"
                )
                return
            scene_id = scene_instance.scene_id
            app_log.info(
                f"场景名称: {scene_data.name}, 场景ID: {scene_id}, 判断类型: {scene_data.conditions.operation}:"
            )

            # 条件判断
            result = self._handle_conditions(
                scene_data.conditions.operation,
                scene_data.conditions,
                other_info,
            )

            # 动作执行
            new_exec_number = scene_instance.exec_number
            if result:
                self._handle_action(scene_id, scene_data.thenActions, log_prefix="THEN")
                new_exec_number = 1
                other_info.once_flag = True
            elif scene_instance.exec_number == 1 and scene_data.elseThenActions:
                self._handle_action(
                    scene_id, scene_data.elseThenActions, log_prefix="ELSE THEN"
                )
                new_exec_number = 0
                other_info.duration_times = 0

            app_log.info(f"{scene_id} 执行完毕\n")
            scene_instance.exec_number = new_exec_number
            scene_instance.other = json.dumps(other_info.dict())
            return scene_instance
        except Exception:
            app_log.error(
                f"{scene_instance.scene_id} 执行智能场景异常 {traceback.format_exc()}"
            )

    def _handle_action(
        self, scene_id, actions: List[SmartSceneAction], log_prefix="THEN"
    ):
        if not actions:
            return
        for action_info in actions:
            action_class = self.action_class_map[action_info.type]
            for child_info in action_info.data:
                ret = action_class.do_func(scene_id=scene_id, data=child_info)
                app_log.info(f"{log_prefix}条件 {child_info} 执行结果: {ret}")

    def _handle_conditions(
        self,
        operation: LogicFunc,
        conditions: SmartSceneCondition,
        other_info: SmartSceneOtherInfo,
    ):
        need_duration_times = conditions.get_duration_info()
        if not self._check_conditions(operation, conditions):
            other_info.duration_times = 0
            return False
        if other_info.duration_times < need_duration_times:
            other_info.duration_times += 1
        app_log.info(
            f"need times: {need_duration_times}, current times: {other_info.duration_times}"
        )
        return other_info.duration_times >= need_duration_times

    def _check_conditions(self, operation, conditions):
        ret_list = []
        for cond in conditions.value:
            parent_type = cond.type  # 父条件类型 (日期、天气、电价)
            condition_class = self.condition_class_map[parent_type]
            ctx = self._build_condition_ctx(cond)
            for child_info in cond.data:
                if child_info.childType == DateConditionType.duration:
                    continue
                ret = condition_class.meet_func(data=child_info, ctx=ctx)
                app_log.info(f"IF条件 {child_info} 判断结果: {ret}")
                ret_list.append(ret)
                # 如果该条件判断不满足，并且客户设置为and,则无需继续判断，返回失败
                if not ret and operation == LogicFunc.AND:
                    return False
                # 如果条件判断满足，并且客户设置为or,则无需继续判断，返回成功
                if ret and operation == LogicFunc.OR:
                    return True
        if (operation == LogicFunc.AND and all(ret_list)) or (
            operation == LogicFunc.OR and any(ret_list)
        ):
            return True
        return False

    @staticmethod
    def _build_condition_ctx(condition_info: ConditionItem):
        ctx = {}
        if condition_info.type == ConditionType.cabinet:
            ctx["cabinet"] = condition_info.cabinet
        return ctx

    def update_all_condition_data(self, condition_types: Set[ConditionType]):
        for cond_type in condition_types:
            self.condition_class_map[cond_type].update_value()
