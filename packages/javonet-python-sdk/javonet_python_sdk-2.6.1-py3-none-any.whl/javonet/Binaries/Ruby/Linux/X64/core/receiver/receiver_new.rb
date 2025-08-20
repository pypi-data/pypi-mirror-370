require_relative '../interpreter/interpreter'
require_relative '../../utils/runtime_logger'
require_relative '../protocol/command_serializer'
require_relative '../../utils/command'
require_relative '../../utils/os_helper'

class Receiver

  def initialize
    puts get_runtime_info
  end

  def send_command(message_array, message_array_len)
    begin
      response_array = CommandSerializer.new.serialize(Interpreter.new.process(message_array))
    rescue Exception => e
      message = "Error occurred in Javonet Ruby Core: #{e.message}"
      puts message
      exception_command = Command.new(RuntimeName::RUBY, CommandType::EXCEPTION, [])
      exception_command = exception_command.add_arg_to_payload(ExceptionType::EXCEPTION)
      exception_command = exception_command.add_arg_to_payload(Command.new(RuntimeName::RUBY, CommandType::EXCEPTION, ["Ruby Core Error", "Ruby Core Error"]).to_string)
      exception_command = exception_command.add_arg_to_payload("Ruby Core Error")
      exception_command = exception_command.add_arg_to_payload(e.message)
      exception_command = exception_command.add_arg_to_payload("Receiver")
      exception_command = exception_command.add_arg_to_payload("send_command")
      exception_command = exception_command.add_arg_to_payload("undefined")
      exception_command = exception_command.add_arg_to_payload(__FILE__)
      response_array = CommandSerializer.new.serialize(exception_command)
    end
      [response_array.length, response_array]
  end

  def heart_beat(message_array, message_array_len)
    response_array = [49, 48]
    [response_array.length, response_array]
  end

  def get_runtime_info
    RuntimeLogger.get_runtime_info(true)
  end
end

