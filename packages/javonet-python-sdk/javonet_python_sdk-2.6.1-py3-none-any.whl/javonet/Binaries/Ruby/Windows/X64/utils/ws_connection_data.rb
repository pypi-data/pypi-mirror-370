class WsConnectionData
  attr_accessor :hostname

  def initialize(hostname)
    @hostname = hostname
  end

  def connection_type
    ConnectionType::WEB_SOCKET
  end

  def serialize_connection_data
    [connection_type, 0, 0, 0, 0, 0, 0]
  end

  def ==(other)
    other.is_a?(WsConnectionData) && @hostname == other.hostname
  end
end
