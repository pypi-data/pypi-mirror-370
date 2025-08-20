"""
The CommandType class represents command types used in communication with Javonet.
"""

# Python 2 doesn't have an enum module, so we implement our own version
class CommandType(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, CommandType):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "CommandType." + str(self)

    Value = None  # These values will be set below
    LoadLibrary = None
    InvokeStaticMethod = None
    GetStaticField = None
    SetStaticField = None
    CreateClassInstance = None
    GetType = None
    Reference = None
    GetModule = None
    InvokeInstanceMethod = None
    Exception = None
    HeartBeat = None
    Cast = None
    GetInstanceField = None
    Optimize = None
    GenerateLib = None
    InvokeGlobalFunction = None
    DestructReference = None
    ArrayReference = None
    ArrayGetItem = None
    ArrayGetSize = None
    ArrayGetRank = None
    ArraySetItem = None
    Array = None
    RetrieveArray = None
    SetInstanceField = None
    InvokeGenericStaticMethod = None
    InvokeGenericMethod = None
    GetEnumItem = None
    GetEnumName = None
    GetEnumValue = None
    AsRef = None
    AsOut = None
    GetRefValue = None
    EnableNamespace = None
    EnableType = None
    CreateNull = None
    GetStaticMethodAsDelegate = None
    GetInstanceMethodAsDelegate = None
    PassDelegate = None
    InvokeDelegate = None
    ConvertType = None
    AddEventListener = None
    PluginWrapper = None
    GetAsyncOperationResult = None

    _name_map = {
        0: 'Value',
        1: 'LoadLibrary',
        2: 'InvokeStaticMethod',
        3: 'GetStaticField',
        4: 'SetStaticField',
        5: 'CreateClassInstance',
        6: 'GetType',
        7: 'Reference',
        8: 'GetModule',
        9: 'InvokeInstanceMethod',
        10: 'Exception',
        11: 'HeartBeat',
        12: 'Cast',
        13: 'GetInstanceField',
        14: 'Optimize',
        15: 'GenerateLib',
        16: 'InvokeGlobalFunction',
        17: 'DestructReference',
        18: 'ArrayReference',
        19: 'ArrayGetItem',
        20: 'ArrayGetSize',
        21: 'ArrayGetRank',
        22: 'ArraySetItem',
        23: 'Array',
        24: 'RetrieveArray',
        25: 'SetInstanceField',
        26: 'InvokeGenericStaticMethod',
        27: 'InvokeGenericMethod',
        28: 'GetEnumItem',
        29: 'GetEnumName',
        30: 'GetEnumValue',
        31: 'AsRef',
        32: 'AsOut',
        33: 'GetRefValue',
        34: 'EnableNamespace',
        35: 'EnableType',
        36: 'CreateNull',
        37: 'GetStaticMethodAsDelegate',
        38: 'GetInstanceMethodAsDelegate',
        39: 'PassDelegate',
        40: 'InvokeDelegate',
        41: 'ConvertType',
        42: 'AddEventListener',
        43: 'PluginWrapper',
        44: 'GetAsyncOperationResult'
    }

# Initialize values
CommandType.Value = CommandType(0)
CommandType.LoadLibrary = CommandType(1)
CommandType.InvokeStaticMethod = CommandType(2)
CommandType.GetStaticField = CommandType(3)
CommandType.SetStaticField = CommandType(4)
CommandType.CreateClassInstance = CommandType(5)
CommandType.GetType = CommandType(6)
CommandType.Reference = CommandType(7)
CommandType.GetModule = CommandType(8)
CommandType.InvokeInstanceMethod = CommandType(9)
CommandType.Exception = CommandType(10)
CommandType.HeartBeat = CommandType(11)
CommandType.Cast = CommandType(12)
CommandType.GetInstanceField = CommandType(13)
CommandType.Optimize = CommandType(14)
CommandType.GenerateLib = CommandType(15)
CommandType.InvokeGlobalFunction = CommandType(16)
CommandType.DestructReference = CommandType(17)
CommandType.ArrayReference = CommandType(18)
CommandType.ArrayGetItem = CommandType(19)
CommandType.ArrayGetSize = CommandType(20)
CommandType.ArrayGetRank = CommandType(21)
CommandType.ArraySetItem = CommandType(22)
CommandType.Array = CommandType(23)
CommandType.RetrieveArray = CommandType(24)
CommandType.SetInstanceField = CommandType(25)
CommandType.InvokeGenericStaticMethod = CommandType(26)
CommandType.InvokeGenericMethod = CommandType(27)
CommandType.GetEnumItem = CommandType(28)
CommandType.GetEnumName = CommandType(29)
CommandType.GetEnumValue = CommandType(30)
CommandType.AsRef = CommandType(31)
CommandType.AsOut = CommandType(32)
CommandType.GetRefValue = CommandType(33)
CommandType.EnableNamespace = CommandType(34)
CommandType.EnableType = CommandType(35)
CommandType.CreateNull = CommandType(36)
CommandType.GetStaticMethodAsDelegate = CommandType(37)
CommandType.GetInstanceMethodAsDelegate = CommandType(38)
CommandType.PassDelegate = CommandType(39)
CommandType.InvokeDelegate = CommandType(40)
CommandType.ConvertType = CommandType(41)
CommandType.AddEventListener = CommandType(42)
CommandType.PluginWrapper = CommandType(43)
CommandType.GetAsyncOperationResult = CommandType(44)