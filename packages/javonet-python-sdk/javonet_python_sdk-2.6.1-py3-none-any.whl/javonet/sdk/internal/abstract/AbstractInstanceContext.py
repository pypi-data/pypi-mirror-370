import abc


class AbstractInstanceContext(abc.ABC):

    @abc.abstractmethod
    def get_instance_field(self, field_name: str):
        pass

    @abc.abstractmethod
    def set_instance_field(self, field_name: str, value):
        pass

    @abc.abstractmethod
    def invoke_instance_method(self, method_name: str, *args):
        pass

    @abc.abstractmethod
    def create_instance(self, *args):
        pass
