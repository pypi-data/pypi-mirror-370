"""
The Type class represents data types used in Javonet.
"""


class Type(object):
    """
    Class representing data types used in Javonet.
    """


    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Type):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "Type." + str(self)

    Command = None
    JavonetString = None
    JavonetInteger = None
    JavonetBoolean = None
    JavonetFloat = None
    JavonetByte = None
    JavonetChar = None
    JavonetLongLong = None
    JavonetDouble = None
    JavonetUnsignedLongLong = None
    JavonetUnsignedInteger = None
    JavonetNoneType = None
    JavonetVoidType = None

    _name_map = {
        0: 'Command',
        1: 'JavonetString',
        2: 'JavonetInteger',
        3: 'JavonetBoolean',
        4: 'JavonetFloat',
        5: 'JavonetByte',
        6: 'JavonetChar',
        7: 'JavonetLongLong',
        8: 'JavonetDouble',
        9: 'JavonetUnsignedLongLong',
        10: 'JavonetUnsignedInteger',
        11: 'JavonetNoneType',
        12: 'JavonetVoidType'
    }

Type.Command = Type(0)
Type.JavonetString = Type(1)
Type.JavonetInteger = Type(2)
Type.JavonetBoolean = Type(3)
Type.JavonetFloat = Type(4)
Type.JavonetByte = Type(5)
Type.JavonetChar = Type(6)
Type.JavonetLongLong = Type(7)
Type.JavonetDouble = Type(8)
Type.JavonetUnsignedLongLong = Type(9)
Type.JavonetUnsignedInteger = Type(10)
Type.JavonetNoneType = Type(11)
Type.JavonetVoidType = Type(12)