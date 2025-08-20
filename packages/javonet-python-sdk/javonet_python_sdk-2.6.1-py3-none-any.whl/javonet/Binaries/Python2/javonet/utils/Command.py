# -*- coding: utf-8 -*-
"""
The Command class represents a command sent to the Javonet runtime environment.
"""

from javonet.utils.CommandType import CommandType


class Command(object):

    def __init__(self, runtime_name, command_type, payload):
        """
        Initializes a new command.

        :param runtime_name: Runtime environment name
        :param command_type: Command type
        :param payload: Command payload
        """
        self.runtime_name = runtime_name
        self.command_type = command_type
        self.payload = payload

    def get_payload(self):
        """
        Returns the command payload.

        :return: Command payload
        """
        return self.payload

    @staticmethod
    def create_response(response, runtime_name):
        """
        Creates a response command.

        :param response: Response
        :param runtime_name: Runtime environment name
        :return: New response command
        """
        return Command(runtime_name, CommandType.Value, [response])

    @staticmethod
    def create_reference(guid, runtime_name):
        """
        Creates a reference command.

        :param guid: GUID identifier
        :param runtime_name: Runtime environment name
        :return: New reference command
        """
        return Command(runtime_name, CommandType.Reference, [guid])

    @staticmethod
    def create_array_response(array, runtime_name):
        """
        Creates an array response command.

        :param array: Array
        :param runtime_name: Runtime environment name
        :return: New array response command
        """
        return Command(runtime_name, CommandType.Array, array)

    def drop_first_payload_argument(self):
        """
        Removes the first argument from the payload.

        :return: New command without the first argument
        """
        payload_args = []
        payload_args.extend(self.payload)
        if len(payload_args) != 0:
            payload_args.pop(0)
        return Command(self.runtime_name, self.command_type, payload_args)

    def add_arg_to_payload(self, argument):
        """
        Adds an argument to the payload.

        :param argument: Argument to add
        :return: New command with the added argument
        """
        merged_payload = self.payload + [argument]
        return Command(self.runtime_name, self.command_type, merged_payload)

    def prepend_arg_to_payload(self, current_command):
        """
        Adds an argument to the beginning of the payload.

        :param current_command: Current command
        :return: New command with the argument added at the beginning
        """
        if current_command is None:
            return Command(self.runtime_name, self.command_type, self.payload)
        else:
            return Command(self.runtime_name, self.command_type, [current_command] + self.payload)

    def to_string(self):
        """
        Returns a text representation of the command.

        :return: Text representation of the command
        """
        return 'Target runtime: ' + str(self.runtime_name) + ' Command type: ' + str(
            self.command_type) + ' Payload: ' + str(self.payload)

    def __eq__(self, other):
        """
        Compare this command with another element.
        
        :param other: Element to compare with
        :return: True if equal, False otherwise
        """
        # Basic comparison
        if not isinstance(other, self.__class__):
            return False
        
        # Compare command_type and runtime_name as numeric values
        if hasattr(self.command_type, 'value') and hasattr(other.command_type, 'value'):
            if self.command_type.value != other.command_type.value:
                return False
        else:
            # If they don't have value attribute, compare directly
            if self.command_type != other.command_type:
                return False
            
        if hasattr(self.runtime_name, 'value') and hasattr(other.runtime_name, 'value'):
            if self.runtime_name.value != other.runtime_name.value:
                return False
        else:
            if self.runtime_name != other.runtime_name:
                return False
        
        # Compare payload length
        if len(self.payload) != len(other.payload):
            return False
        
        # Compare each payload item
        for i in range(len(self.payload)):
            # For simple types
            if self.payload[i] != other.payload[i]:
                return False
                
        return True

    def __str__(self):
        """
        String representation of the command.
        
        :return: String representation
        """
        return "Command(type={0}, runtime={1}, payload_len={2})".format(
            self.command_type, self.runtime_name, len(self.payload))
        
    def __repr__(self):
        """
        Detailed representation of the command.
        
        :return: Detailed representation
        """
        return self.__str__()

    def __ne__(self, element):
        """
        Compare this command with another element for inequality.
        
        :param element: Element to compare with
        :return: True if not equal, False otherwise
        """
        return not self.__eq__(element)