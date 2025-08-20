"""
The StringEncodingMode class represents character encoding modes used in Javonet.
"""

class StringEncodingMode(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, StringEncodingMode):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "StringEncodingMode." + str(self)

    ASCII = None
    UTF8 = None
    UTF16 = None
    UTF32 = None

    _name_map = {
        0: 'ASCII',
        1: 'UTF8',
        2: 'UTF16',
        3: 'UTF32'
    }

StringEncodingMode.ASCII = StringEncodingMode(0)
StringEncodingMode.UTF8 = StringEncodingMode(1)
StringEncodingMode.UTF16 = StringEncodingMode(2)
StringEncodingMode.UTF32 = StringEncodingMode(3) 