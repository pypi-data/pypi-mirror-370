from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.connectionData.InMemoryConnectionData import InMemoryConnectionData
from javonet.utils.Command import Command
from javonet.utils.exception.ExceptionThrower import ExceptionThrower


class PassDelegateHandler(AbstractCommandHandler):
    _required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception(f"{self.__class__.__name__} parameters mismatch")

            delegate_guid = command.payload[0]
            calling_runtime = RuntimeName(command.payload[1])

            # not used in this context, but kept for reference
            #parameters_from_command = command.payload[2:] if len(command.payload) > 2 else []
            #delegate_param_types = parameters_from_command[:-1]
            #delegate_return_type = parameters_from_command[-1] if parameters_from_command else None

            def dynamic_delegate(*args):
                # Prepare the command to invoke the delegate
                args_array = [delegate_guid] + list(args)
                invoke_delegate_command = Command(
                    calling_runtime,
                    CommandType.InvokeDelegate,
                    args_array
                )
                from javonet.core.interpreter.Interpreter import Interpreter
                response = Interpreter().execute(invoke_delegate_command, InMemoryConnectionData())
                if response.command_type == CommandType.Exception:
                    raise Exception("Exception occurred while invoking delegate:\n" + str(ExceptionThrower.throw_exception(response)))

                # not used in this context, but kept for reference
                # if delegate_return_type is not None and delegate_return_type.__name__ == "JavonetVoidType":
                #     return None

                return response.payload[0] if response.payload else None

            return dynamic_delegate

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None