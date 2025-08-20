class TypesHandler:

    def __init__(self):
        pass

    @staticmethod
    def is_primitive_or_none(item):
        return isinstance(item, (int, long, float, bool, str, unicode)) or item is None
