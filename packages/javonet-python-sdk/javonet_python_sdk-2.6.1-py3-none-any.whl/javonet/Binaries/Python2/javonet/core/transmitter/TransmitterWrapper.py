import os
import platform
from ctypes import *
from javonet.core.callback.callbackFunc import callbackFunc

CMPFUNC = CFUNCTYPE(py_object, POINTER(c_ubyte), c_int)
callbackFunction = CMPFUNC(callbackFunc)


class TransmitterWrapper:
    _python_lib = None

    @staticmethod
    def get_native_lib():
        if TransmitterWrapper._python_lib is None:
            file_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            machine = platform.machine().lower()
            if '64' in machine:
                arch = 'X64'
            elif 'arm' in machine:
                arch = 'ARM64' if '64' in machine else 'ARM'
            else:
                arch = 'X86'

            system_name = platform.system()
            if system_name == 'Windows':
                python_lib_path = file_path + '/Binaries/Native/Windows/{0}/JavonetPython2RuntimeNative.dll'.format(arch)
            elif system_name == 'Linux':
                python_lib_path = file_path + '/Binaries/Native/Linux/{0}/libJavonetPython2RuntimeNative.so'.format(arch)
            elif system_name == 'Darwin':
                python_lib_path = file_path + '/Binaries/Native/MacOs/{0}/libJavonetPython2RuntimeNative.dylib'.format(arch)
            else:
                raise RuntimeError("Unsupported OS: " + system_name)
            lib = cdll.LoadLibrary(python_lib_path)
            lib.SetCallback(callbackFunction)
            TransmitterWrapper._python_lib = lib
        return TransmitterWrapper._python_lib

    @staticmethod
    def send_command(message):
        lib = TransmitterWrapper.get_native_lib()
        message_array = bytearray(message)
        message_ubyte_array = (c_ubyte * len(message_array))
        response_array_len = lib.SendCommand(message_ubyte_array.from_buffer(message_array), len(message_array))
        if response_array_len > 0:
            response = bytearray(response_array_len)
            response_ubyte_array = (c_ubyte * response_array_len)
            lib.ReadResponse(response_ubyte_array.from_buffer(response), response_array_len)
            return response
        elif response_array_len == 0:
            raise RuntimeError("Response is empty")
        else:
            lib.GetNativeError.restype = c_char_p
            lib.GetNativeError.argtypes = []
            error_message = lib.GetNativeError()
            raise RuntimeError("Javonet native error code: {0}. {1}".format(response_array_len, error_message))

    @staticmethod
    def activate(license_key):
        lib = TransmitterWrapper.get_native_lib()
        activate_func = lib.Activate
        activate_func.restype = c_int
        activate_func.argtypes = [c_char_p]
        # In Python 2, you can still use encode() to ensure a byte string.
        activation_result = activate_func(license_key.encode('ascii'))
        if activation_result < 0:
            lib.GetNativeError.restype = c_char_p
            lib.GetNativeError.argtypes = []
            error_message = lib.GetNativeError()
            raise RuntimeError("Javonet activation result: {0}. Native error message: {1}".format(activation_result, error_message))
        else:
            return activation_result

    @staticmethod
    def set_config_source(source_path):
        lib = TransmitterWrapper.get_native_lib()
        set_config_source_func = lib.SetConfigSource
        set_config_source_func.restype = c_int
        set_config_source_func.argtypes = [c_char_p]
        set_config_result = set_config_source_func(source_path.encode('utf-8'))
        if set_config_result < 0:
            lib.GetNativeError.restype = c_char_p
            lib.GetNativeError.argtypes = []
            error_message = lib.GetNativeError()
            raise RuntimeError("Javonet set config source result: {0}. Native error message: {1}".format(set_config_result, error_message))
        else:
            return set_config_result

    @staticmethod
    def set_javonet_working_directory(path):
        lib = TransmitterWrapper.get_native_lib()
        set_working_directory_func = lib.SetWorkingDirectory
        set_working_directory_func.restype = c_int
        set_working_directory_func.argtypes = [c_char_p]
        set_working_directory_result = set_working_directory_func(path.encode('utf-8'))
        if set_working_directory_result < 0:
            lib.GetNativeError.restype = c_char_p
            lib.GetNativeError.argtypes = []
            error_message = lib.GetNativeError()
            raise RuntimeError("Javonet set working directory result: {0}. Native error message: {1}".format(set_working_directory_result, error_message))
        else:
            return set_working_directory_result