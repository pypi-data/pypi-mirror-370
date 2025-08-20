require_relative '../reference_cache/references_cache'
require_relative 'abstract_command_handler'
require_relative '../../utils/runtime_name'
require_relative '../../utils/command'

class ResolveInstanceHandler < AbstractCommandHandler
  def initialize
    @required_parameters_count = 1
  end

  def process(command)
    resolve_reference(command)
  end

  def resolve_reference(command)
    if command.payload.length != @required_parameters_count
      raise ArgumentError.new "Resolve Instance parameters mismatch"
    end
    begin
      if command.runtime_name == RuntimeName::RUBY
        return ReferencesCache.instance.resolve_reference(command.payload[0])
      else
        return new Command(command.runtime_name, CommandType::REFERENCE, command.payload[0])
      end
    rescue Exception => ex
      return ex
    end
  end
end
