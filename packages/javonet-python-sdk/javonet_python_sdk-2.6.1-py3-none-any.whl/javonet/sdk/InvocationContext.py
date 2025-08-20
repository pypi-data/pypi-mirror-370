import types
from argparse import ArgumentError
from threading import Thread

from javonet.core.delegateCache.DelegatesCache import DelegatesCache
from javonet.utils.Type import Type
from javonet.utils.TypesHandler import TypesHandler
from javonet.utils.messageHelper.MessageHelper import MessageHelper
from javonet.utils.connectionData.IConnectionData import IConnectionData
from javonet.utils.exception.ExceptionThrower import ExceptionThrower
from javonet.core.interpreter.Interpreter import Interpreter
from javonet.sdk.InvocationContextEnum import InvocationContextEnum
from javonet.sdk.internal.abstract.AbstractInstanceContext import AbstractInstanceContext
from javonet.sdk.internal.abstract.AbstractInvocationContext import AbstractInvocationContext
from javonet.sdk.internal.abstract.AbstractMethodInvocationContext import AbstractMethodInvocationContext
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName


class InvocationContext(AbstractInvocationContext, AbstractMethodInvocationContext, AbstractInstanceContext):
    """
    InvocationContext is a class that represents a context for invoking commands.
    It implements several interfaces for different types of interactions.
    This class is used to construct chains of invocations, representing expressions of interaction that have not yet been executed.

    Returns:
        InvocationContext: The new instance of InvocationContext.

    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/invocation-context>`_
    """

    def __init__(self, runtime_name: RuntimeName,
                 connection_data: IConnectionData,
                 current_command: Command, is_executed=False):
        self.__is_executed = is_executed
        self.__runtime_name = runtime_name
        self.__connection_data = connection_data
        self.__current_command = current_command
        self.__python_interpreter = Interpreter()

    #def __del__(self):
    #    if self.__current_command.command_type == CommandType.Reference and self.__is_executed is True:
    #        self.__current_command = Command(self.__runtime_name, CommandType.DestructReference,
    #                                         self.__current_command.payload)
    #        self.execute()

    def get_current_command(self):
        return self.__current_command

    def __iter__(self):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__iter__()

    def __next__(self):
        if self.__current_command.command_type != CommandType.Reference:
            raise Exception("Object is not iterable")
        else:
            return self.__invocation_context_enum.__next__()

    def __getitem__(self, key):
        if self.__current_command.command_type not in [CommandType.Reference, CommandType.ArrayGetItem]:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__getitem__(key)

    def __setitem__(self, key, value):
        if self.__current_command.command_type not in [CommandType.Reference, CommandType.ArrayGetItem,
                                                       CommandType.ArraySetItem]:
            raise Exception("Object is not iterable")
        else:
            self.__invocation_context_enum = InvocationContextEnum(self)
            return self.__invocation_context_enum.__setitem__(key, value)

    def execute(self):
        """
        Executes the current command.
        Because invocation context is building the intent of executing particular expression on target environment, we call the initial state of invocation context as non-materialized. 
        The non-materialized context wraps either single command or chain of recursively nested commands.
        Commands are becoming nested through each invocation of methods on Invocation Context.
        Each invocation triggers the creation of new Invocation Context instance wrapping the current command with new parent command valid for invoked method.
        Developer can decide on any moment of the materialization for the context taking full control of the chunks of the expression being transferred and processed on target runtime.

        Returns:
            InvocationContext: The InvocationContext after executing the command.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/execute-method>`_
        """
        response_command = self.__python_interpreter.execute(self.__current_command,
                                                             self.__connection_data)

        if response_command.command_type == CommandType.Exception:
            exception = ExceptionThrower.throw_exception(response_command)
            MessageHelper.send_message_to_app_insights("SdkException", str(exception))
            raise exception

        if self.__current_command.command_type == CommandType.CreateClassInstance:
            self.__current_command = response_command
            self.__is_executed = True
            return self

        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 response_command, True)

    def execute_async(self):
        """
        Executes the current command asynchronously.

        Returns:
            InvocationContext: The InvocationContext after executing the command asynchronously.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/execute-method>`_
        """
        thread = Thread(target=self.execute)
        thread.start()
        return thread


    def invoke_static_method(self, method_name: str, *args: object):
        """
        Invokes a static method on the target runtime.

        Args:
            method_name: The name of the static method to invoke.
            args: The arguments to pass to the static method.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to invoke the static method.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/calling-methods/invoking-static-method>`_
        """
        local_command = Command(self.__runtime_name, CommandType.InvokeStaticMethod, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def invoke_instance_method(self, method_name: str, *args: object):
        """
        Invokes an instance method on the target runtime.

        Args:
            method_name: The name of the instance method to invoke.
            args: The arguments to pass to the instance method.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to invoke the instance method.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/calling-methods/creating-instance-and-calling-instance-methods>`_
        """
        local_command = Command(self.__runtime_name, CommandType.InvokeInstanceMethod, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_static_field(self, field_name: str):
        """
        Gets the value of a static field from the target runtime.

        Args:
            field_name: The name of the static field to get.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to get the static field.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/fields-and-properties/getting-and-setting-values-for-static-fields-and-properties>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetStaticField, [field_name])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def set_static_field(self, field_name: str, value: object):
        """
        Sets the value of a static field in the target runtime.

        Args:
            field_name: The name of the static field to set.
            value: The new value to set.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to set the static field.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/fields-and-properties/getting-and-setting-values-for-static-fields-and-properties>`_
        """
        local_command = Command(self.__runtime_name, CommandType.SetStaticField, [field_name, value])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def create_instance(self, *args: object):
        """
        Invokes a constructor on the target runtime.

        Args:
            args: Class constructor arguments.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to invoke the constructor.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/calling-methods/creating-instance-and-calling-instance-methods>`_
        """
        local_command = Command(self.__runtime_name, CommandType.CreateClassInstance, [*args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_instance_field(self, field_name: str):
        """
        Retrieves the value of an instance field from the target runtime.

        Args:
            field_name: The name of the instance field to get.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to get the instance field.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/fields-and-properties/getting-and-setting-values-for-instance-fields-and-properties>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetInstanceField, [field_name])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def set_instance_field(self, field_name: str, value: object):
        """
        Sets the value of an instance field in the target runtime.

        Args:
            field_name: The name of the instance field to set.
            value: The new value to set.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to set the instance field.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/fields-and-properties/getting-and-setting-values-for-instance-fields-and-properties>`_
        """
        local_command = Command(self.__runtime_name, CommandType.SetInstanceField, [field_name, value])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_index(self, *indexes: object):
        """
        Retrieves the value at a specified index in an array from the target runtime.

        Args:
            indexes: The arguments to pass to the array getter. They should be the indexes.

        Returns:
            InvocationContext: A new InvocationContext instance that wraps the command to get the array element.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/arrays-and-collections/multidimensional-arrays>`_
        """
        local_command = Command(self.__runtime_name, CommandType.ArrayGetItem, [*indexes])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def set_index(self, indexes: object, value: object):
        """
        Sets the value at a specified index in an array on the target runtime.

        Args:
            indexes: The arguments to pass to the array setter. They should be the indexes.
            value: The new value to set.

        Returns:
            InvocationContext: An InvocationContext instance with the command to set the array element.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/arrays-and-collections/one-dimensional-arrays>`_
        """
        local_command = Command(self.__runtime_name, CommandType.ArraySetItem, [indexes, value])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_size(self):
        """
        Retrieves the number of elements in the array from the target runtime.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the array size.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/arrays-and-collections/one-dimensional-arrays>`_
        """
        local_command = Command(self.__runtime_name, CommandType.ArrayGetSize, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_rank(self):
        """
        Retrieves the rank (number of dimensions) of an array from the target runtime.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the array rank.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/arrays-and-collections/multidimensional-arrays>`_
        """
        local_command = Command(self.__runtime_name, CommandType.ArrayGetRank, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def invoke_generic_static_method(self, method_name: str, *args: object):
        """
        Invokes a generic static method on the target runtime.

        Args:
            method_name: The name of the generic static method to invoke.
            args: The arguments to pass to the generic static method. Depends on called runtime technology.

        Returns:
            InvocationContext: An InvocationContext instance with the command to invoke the generic static method.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/generics/calling-generic-static-method>`_
        """
        local_command = Command(self.__runtime_name, CommandType.InvokeGenericStaticMethod, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def invoke_generic_method(self, method_name: str, *args: object):
        """
        Invokes a generic instance method on the target runtime.

        Args:
            method_name: The name of the generic instance method to invoke.
            args: The arguments to pass to the generic instance method. Depends on called runtime technology.

        Returns:
            InvocationContext: An InvocationContext instance with the command to invoke the generic instance method.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/generics/calling-generic-static-method>`_
        """
        local_command = Command(self.__runtime_name, CommandType.InvokeGenericMethod, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_enum_name(self):
        """
        Retrieves the name of an enum value from the target runtime.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the enum name.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/enums/using-enum-type>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetEnumName, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_enum_value(self):
        """
        Retrieves the value of an enum from the target runtime.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/enums/using-enum-type>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetEnumValue, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_ref_value(self):
        """
        Retrieves the value of a reference type argument from the target runtime.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the reference value.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/net-dll/methods-arguments/passing-arguments-by-reference-with-ref-keyword>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetRefValue, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def create_null(self):
        """
        Creates a null object on the of a specific type on the target runtime.

        Returns:
            InvocationContext: An InvocationContext instance with the command to create a null object.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/null-handling/create-null-object>`_
        """
        local_command = Command(self.__runtime_name, CommandType.CreateNull, [])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_static_method_as_delegate(self, method_name: str, *args: object):
        """
        Retrieves a static method as a delegate from the target runtime.

        Args:
            method_name: The name of the static method to retrieve as a delegate.
            args: The arguments to pass to the static method.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the static method as a delegate.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/delegates-and-events/using-delegates>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetStaticMethodAsDelegate, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_instance_method_as_delegate(self, method_name: str, *args: object):
        """
        Retrieves an instance method as a delegate from the target runtime.

        Args:
            method_name: The name of the instance method to retrieve as a delegate.
            args: The arguments to pass to the instance method.

        Returns:
            InvocationContext: An InvocationContext instance with the command to get the instance method as a delegate.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/delegates-and-events/using-delegates>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetInstanceMethodAsDelegate, [method_name, *args])
        return InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))

    def get_value(self):
        """
        Returns the primitive value from the target runtime. This could be any primitive type in Python, 
        such as int, bool, byte, char, long, double, float, etc.

        Returns:
            The value from the target runtime.
        """
        return self.__current_command.payload[0]

    def retrieve_array(self):
        """
        Retrieves an array from the target runtime.

        Returns:
            The retrieved array.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/arrays-and-collections/one-dimensional-arrays>`_
        """
        local_command = Command(self.__runtime_name, CommandType.RetrieveArray, [])
        local_inv_ctx = InvocationContext(self.__runtime_name, self.__connection_data,
                                          self.__build_command(local_command))
        array_inv_ctx = local_inv_ctx.execute()
        return array_inv_ctx.__current_command.get_payload()

    def get_result_type(self) -> str:
        """
        Retrieves the type of the object from the target runtime.

        Returns:
            str: The type of the object.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/type-handling/getting-object-type>`_
        """
        local_command = Command(self.__runtime_name, CommandType.GetResultType, [])
        ic = InvocationContext(self.__runtime_name, self.__connection_data,
                                 self.__build_command(local_command))
        return ic.execute().get_value()

    def get_runtime_name(self) -> RuntimeName:
        """
        Retrieves the name of the runtime where the command is executed.

        Returns:
            RuntimeName: The name of the runtime.

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/runtime-name>`_
        """
        return self.__runtime_name

    def __build_command(self, command):
        for i in range(len(command.payload)):
            command.payload[i] = self.__encapsulate_payload_item(command.payload[i])

        return command.prepend_arg_to_payload(self.__current_command)

    # encapsulate payload item into command
    def __encapsulate_payload_item(self, payload_item):
        if isinstance(payload_item, Command):
            for i in range(len(payload_item.payload)):
                payload_item.payload[i] = self.__encapsulate_payload_item(payload_item.payload[i])
            return payload_item

        elif isinstance(payload_item, InvocationContext):
            return payload_item.get_current_command()

        elif isinstance(payload_item, list):
            copied_payload = [self.__encapsulate_payload_item(item) for item in payload_item]
            return Command(self.__runtime_name, CommandType.Array, copied_payload)

        elif isinstance(payload_item, Type):
            return Command(self.__runtime_name, CommandType.ConvertType, [payload_item])

        elif isinstance(payload_item, types.FunctionType):
            arg_count = payload_item.__code__.co_argcount
            #TO BE CHANGED
            types_list = [Command(self.__runtime_name, CommandType.ConvertType, ["object"])] * (arg_count + 1)
            delegate_id = DelegatesCache().add_delegate(payload_item)
            args = [delegate_id, RuntimeName.python.value] + types_list

            for i in range(len(args)):
                args[i] = self.__encapsulate_payload_item(args[i])
            return Command(self.__runtime_name, CommandType.PassDelegate, args)

        elif TypesHandler.is_primitive_or_none(payload_item):
            return Command(self.__runtime_name, CommandType.Value, [payload_item])
        else:
            raise TypeError(f"Unsupported payload item type: {type(payload_item)} for payload item: {payload_item}.")
