require_relative 'type_serializer'
require_relative '../../utils/command'
require_relative '../../utils/runtime_name'
require_relative '../../utils/tcp_connection_data'

class CommandSerializer
  def serialize(root_command, connection_data = nil, runtime_version = 0)
    buffer = []
    buffer << root_command.runtime_name
    buffer << runtime_version

    if connection_data
      buffer.concat(connection_data.serialize_connection_data)
    else
      buffer.concat([0, 0, 0, 0, 0, 0, 0])
    end

    buffer << RuntimeName::RUBY
    buffer << root_command.command_type

    serialize_recursively(root_command, buffer)
    buffer
  end

  def serialize_recursively(command, buffer)
    command.payload.each do |item|
      if item.is_a?(Command)
        buffer.concat(TypeSerializer.serialize_command(item))
        serialize_recursively(item, buffer)
      elsif TypesHandler.primitive_or_none?(item)
        buffer.concat(TypeSerializer.serialize_primitive(item))
      else
        cached_reference = ReferencesCache.new.cache_reference(item)
        ref_command = Command.new(RuntimeName::RUBY, CommandType::REFERENCE, cached_reference)
        serialize_recursively(ref_command, buffer)
      end
    end
  end
end
