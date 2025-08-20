import abc


class AbstractTypeContext(abc.ABC):

    @abc.abstractmethod
    def get_type(self, type_name: str, *args):
        pass
