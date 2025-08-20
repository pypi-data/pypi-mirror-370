"""
The RuntimeName class represents available runtime environments in Javonet.
"""

# -*- coding: utf-8 -*-

# RuntimeName enumeration with the same values as in Python 3 version
class RuntimeName(object):
    """
    Enumeration of runtime names.
    """
    # Keep the exact same values as in the original
    clr = 0
    go = 1
    jvm = 2
    netcore = 3
    perl = 4
    python = 5
    ruby = 6
    nodejs = 7
    cpp = 8
    php = 9
    python27 = 10
    
    # Static instances to mimic Enum behavior
    CLR = 0
    GO = 1
    JVM = 2
    NETCORE = 3
    PERL = 4
    PYTHON = 5
    RUBY = 6
    NODEJS = 7
    CPP = 8
    PHP = 9
    PYTHON27 = 10

    def __init__(self, value=None):
        """
        Initialize with a value.
        
        :param value: Runtime value
        """
        self.value = value
    
    # Map of names to values
    _name_map = {
        'clr': 0,
        'go': 1,
        'jvm': 2,
        'netcore': 3,
        'perl': 4,
        'python': 5,
        'ruby': 6,
        'nodejs': 7,
        'cpp': 8,
        'php': 9,
        'python27': 10
    }
    
    # Map of values to names
    _value_map = {
        0: 'clr',
        1: 'go',
        2: 'jvm',
        3: 'netcore',
        4: 'perl',
        5: 'python',
        6: 'ruby',
        7: 'nodejs',
        8: 'cpp',
        9: 'php',
        10: 'python27'
    }
    
    @classmethod
    def from_name(cls, name):
        """
        Get runtime by name.
        
        :param name: Runtime name
        :return: Runtime value
        """
        return cls._name_map.get(name.lower())
    
    @classmethod
    def to_name(cls, value):
        """
        Get name by runtime value.
        
        :param value: Runtime value
        :return: Runtime name
        """
        return cls._value_map.get(value)

    def __eq__(self, other):
        if isinstance(other, RuntimeName):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "RuntimeName." + str(self)

RuntimeName.clr = RuntimeName(0)
RuntimeName.go = RuntimeName(1)
RuntimeName.jvm = RuntimeName(2)
RuntimeName.netcore = RuntimeName(3)
RuntimeName.perl = RuntimeName(4)
RuntimeName.python = RuntimeName(5)
RuntimeName.ruby = RuntimeName(6)
RuntimeName.nodejs = RuntimeName(7)
RuntimeName.cpp = RuntimeName(8)
RuntimeName.php = RuntimeName(9)
RuntimeName.python27 = RuntimeName(10)