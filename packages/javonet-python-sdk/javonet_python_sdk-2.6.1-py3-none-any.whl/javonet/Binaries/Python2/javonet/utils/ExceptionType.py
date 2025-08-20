"""
The ExceptionType class represents exception types used in Javonet.
"""

class ExceptionType(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ExceptionType):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "ExceptionType." + str(self)

    Exception = None
    IOException = None
    FileNotFoundException = None
    RuntimeException = None
    ArithemticException = None
    IllegalArgumentException = None
    IndexOutOfBoundsException = None
    NullPointerException = None
    ZeroDivisionException = None

    _name_map = {
        0: 'Exception',
        1: 'IOException',
        2: 'FileNotFoundException',
        3: 'RuntimeException',
        4: 'ArithemticException',
        5: 'IllegalArgumentException',
        6: 'IndexOutOfBoundsException',
        7: 'NullPointerException',
        8: 'ZeroDivisionException'
    }

    @staticmethod
    def to_enum(exception_name):
        if exception_name == "Exception":
            return ExceptionType.Exception.value
        if exception_name == "IOError":
            return ExceptionType.IOException.value
        if exception_name == "IOError":  # In Python 2 FileNotFoundError is IOError
            return ExceptionType.FileNotFoundException.value
        if exception_name == "RuntimeError":
            return ExceptionType.RuntimeException.value
        if exception_name == "ArithmeticError":
            return ExceptionType.ArithemticException.value
        if exception_name == "IndexError":
            return ExceptionType.IndexOutOfBoundsException.value
        if exception_name == "AttributeError":
            return ExceptionType.NullPointerException.value
        if exception_name == "ZeroDivisionError":
            return ExceptionType.ZeroDivisionException.value
        else:
            return ExceptionType.Exception.value

    @staticmethod
    def to_exception(exception_enum):
        if exception_enum == ExceptionType.Exception.value:
            return Exception
        if exception_enum == ExceptionType.IOException.value:
            return IOError
        if exception_enum == ExceptionType.FileNotFoundException.value:
            return IOError  # In Python 2 we use IOError instead of FileNotFoundError
        if exception_enum == ExceptionType.RuntimeException.value:
            return RuntimeError
        if exception_enum == ExceptionType.ArithemticException.value:
            return ArithmeticError
        if exception_enum == ExceptionType.IndexOutOfBoundsException.value:
            return IndexError
        if exception_enum == ExceptionType.NullPointerException.value:
            return AttributeError
        if exception_enum == ExceptionType.ZeroDivisionException.value:
            return ZeroDivisionError
        else:
            return Exception

ExceptionType.Exception = ExceptionType(0)
ExceptionType.IOException = ExceptionType(1)
ExceptionType.FileNotFoundException = ExceptionType(2)
ExceptionType.RuntimeException = ExceptionType(3)
ExceptionType.ArithemticException = ExceptionType(4)
ExceptionType.IllegalArgumentException = ExceptionType(5)
ExceptionType.IndexOutOfBoundsException = ExceptionType(6)
ExceptionType.NullPointerException = ExceptionType(7)
ExceptionType.ZeroDivisionException = ExceptionType(8) 