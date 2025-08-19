class BaseCondition(object):
    condition_type = None

    def __init__(self, update_value_function, **kwargs):
        self.value = {}
        if not callable(update_value_function):
            raise ValueError("update_value_function must be callable")
        self.update_value_function = update_value_function

    def update_value(self):
        new_value = self.update_value_function()
        if not isinstance(new_value, dict):
            raise ValueError("update_value_function must return a dict")
        self.value.update(new_value)

    def meet_func(self, data, ctx):
        ...
