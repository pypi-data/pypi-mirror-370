from solax_py_library.smart_scene.core.action.base import BaseAction
from solax_py_library.smart_scene.types.action import ActionType


class SystemAction(BaseAction):
    action_type = ActionType.system
