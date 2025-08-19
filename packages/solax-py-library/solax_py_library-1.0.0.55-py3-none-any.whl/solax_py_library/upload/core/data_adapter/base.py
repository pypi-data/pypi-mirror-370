from abc import ABCMeta, abstractmethod


class BaseDataAdapter(metaclass=ABCMeta):
    data_type = None

    @abstractmethod
    def parse_data(self, data):
        ...
