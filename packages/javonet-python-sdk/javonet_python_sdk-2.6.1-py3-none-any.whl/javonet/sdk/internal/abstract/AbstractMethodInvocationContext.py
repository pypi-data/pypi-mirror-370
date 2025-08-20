import abc


class AbstractMethodInvocationContext(abc.ABC):

    @abc.abstractmethod
    def invoke_static_method(self, method_name: str, *args):
        pass

    @abc.abstractmethod
    def get_static_field(self, field_name: str):
        pass
