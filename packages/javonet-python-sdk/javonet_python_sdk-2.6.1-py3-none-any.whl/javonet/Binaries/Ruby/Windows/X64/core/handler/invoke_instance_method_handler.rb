require_relative 'abstract_command_handler'

class InvokeInstanceMethodHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 2
  end

  def process(command)
    invoke_instance_method(command)
  end

  def invoke_instance_method(command)
    begin
      if command.payload.length < @required_parameters_count
        raise ArgumentError.new "InvokeInstanceMethod parameters mismatch"
      end

      instance = command.payload[0]
      method_name = command.payload[1]

      if command.payload.length > 2
        arguments = command.payload[2..]
        return instance.send(method_name, *arguments)
      else
        return instance.send(method_name)
      end
    rescue NoMethodError
      methods = instance.methods
      message = "Method #{method_name} not found in object of class #{instance.class.name}. Available methods:\n"
      methods.each { |method_iter| message += "#{method_iter}\n" }
      raise Exception, message
    rescue Exception => e
      return e
    end
  end
end