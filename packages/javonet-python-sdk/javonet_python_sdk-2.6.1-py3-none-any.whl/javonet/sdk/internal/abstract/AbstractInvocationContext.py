import abc


class AbstractInvocationContext(abc.ABC):
    import abc

    class AbstractInvocationContext(abc.ABC):

        @abc.abstractmethod
        def execute(self):
            pass

        @abc.abstractmethod
        def execute_async(self):
            pass

        @abc.abstractmethod
        def invoke_static_method(self, method_name: str, value: object):
            pass

        @abc.abstractmethod
        def invoke_instance_method(self, method_name: str, *args: object):
            pass

        @abc.abstractmethod
        def get_static_field(self, field_name: str):
            pass

        @abc.abstractmethod
        def set_static_field(self, field_name: str, value: object):
            pass

        @abc.abstractmethod
        def create_instance(self, *args: object):
            pass

        @abc.abstractmethod
        def get_instance_field(self, field_name: str):
            pass

        @abc.abstractmethod
        def set_instance_field(self, field_name: str, value: object):
            pass

        @abc.abstractmethod
        def get_index(self, *indexes: object):
            pass

        @abc.abstractmethod
        def set_index(self, indexes: object, value: object):
            pass

        @abc.abstractmethod
        def get_size(self):
            pass

        @abc.abstractmethod
        def get_rank(self):
            pass

        @abc.abstractmethod
        def invoke_generic_static_method(self, method_name: str, *args: object):
            pass

        @abc.abstractmethod
        def invoke_generic_method(self, method_name: str, *args: object):
            pass

        @abc.abstractmethod
        def get_enum_name(self):
            pass

        @abc.abstractmethod
        def get_enum_value(self):
            pass

        @abc.abstractmethod
        def get_ref_value(self):
            pass

        @abc.abstractmethod
        def get_value(self):
            pass

        @abc.abstractmethod
        def retrieve_array(self):
            pass
