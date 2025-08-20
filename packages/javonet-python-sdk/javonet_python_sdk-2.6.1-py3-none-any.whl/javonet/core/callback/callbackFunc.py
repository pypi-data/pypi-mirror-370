from ctypes import *

def callbackFunc(message_byte_array, message_byte_array_len):
    message_byte_array_py = bytearray((c_ubyte * message_byte_array_len).from_address(
        addressof(message_byte_array.contents)))
    message_byte_array_len_py = int(message_byte_array_len)
    from javonet.core.receiver.Receiver import Receiver
    python_receiver = Receiver()
    if message_byte_array[10] == 11:
        return python_receiver.HeartBeat(message_byte_array_py, message_byte_array_len_py)
    else:
        return python_receiver.SendCommand(message_byte_array_py, message_byte_array_len_py)
