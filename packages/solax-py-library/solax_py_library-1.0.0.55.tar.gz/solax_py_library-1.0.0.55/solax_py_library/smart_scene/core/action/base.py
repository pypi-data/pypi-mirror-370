class BaseAction(object):
    def __init__(self, do_funcs, **kwargs):
        self.do_func_map = do_funcs

    def do_func(self, scene_id, data):
        child_data = data.childData
        child_type = data.childType
        do_func = self.do_func_map.get(child_type)
        return do_func(scene_id, child_data.data)
