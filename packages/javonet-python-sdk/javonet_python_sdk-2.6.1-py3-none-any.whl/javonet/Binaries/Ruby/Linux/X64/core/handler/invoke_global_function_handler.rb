require_relative 'abstract_command_handler'

class InvokeGlobalFunctionHandler < AbstractCommandHandler
  def process(command)
    invoke_function(command)
  end

  def invoke_function(command)
    begin
      payload = command.payload
      raise ArgumentError, "InvokeGlobalFunction requires at least one parameter" if payload.empty?

      # Expect the first parameter to be a string in the form "ModuleName.function_name"
      full_method_string = payload[0]
      unless full_method_string.is_a?(String) && full_method_string.include?(".")
        raise ArgumentError, "Expected a string in the format 'ModuleName.function_name'"
      end

      parts = full_method_string.split(".")
      if parts.size < 2
        raise ArgumentError, "Invalid function identifier format. Expected 'ModuleName.function_name'"
      end

      function_name = parts.pop
      module_name = parts.join("::") # Convert dot-separated names to Ruby's "::" notation

      begin
        target = Object.const_get(module_name)
      rescue NameError => e
        raise NameError, "Module/Class #{module_name} not found: #{e.message}"
      end

      args = payload[1..-1] || []

      if target.respond_to?(function_name)
        target.send(function_name, *args)
      else
        available_methods = target.methods.join(', ')
        raise NoMethodError, "Method #{function_name} not found in module #{module_name}. Available methods: #{available_methods}"
      end
    rescue Exception => e
      e
    end
  end
end
