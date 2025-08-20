require 'websocket'
require 'uri'

class WebSocketClient
  def initialize(url)
    @uri = URI.parse(url)
    raise "Only ws:// or wss:// URLs are supported" unless %w[ws wss].include?(@uri.scheme)

    @host = @uri.host
    @port = @uri.port || default_port
    @path = @uri.path.empty? ? '/' : @uri.path
    @path += "?#{@uri.query}" if @uri.query

    @socket = open_socket
    @handshake = WebSocket::Handshake::Client.new(
      url: url
    )

    perform_handshake
  end

  def send_message(message)
    frame = WebSocket::Frame::Outgoing::Client.new(version: @handshake.version, data: message.pack("C*"), type: :binary)
    @socket.write(frame.to_s)
  end

  def receive_message(timeout: 5)
    buffer = ''
    start_time = Time.now

    while Time.now - start_time < timeout
      if IO.select([@socket], nil, nil, 0.1)
        chunk = @socket.read_nonblock(1024, exception: false)
        break if chunk.nil?

        buffer << chunk
        frame = WebSocket::Frame::Incoming::Client.new(version: @handshake.version)
        frame << buffer
        data = frame.next
        return data.data.bytes if data
      end
    end

    nil
  end

  def self.add_or_get_client(url)
    @@clients ||= {}
    client = @@clients[url]
    if client.nil? || !client.open?
      client&.close
      client = new(url)
      @@clients[url] = client
    end
    client
  end

  def self.send_message(url, message)
    client = add_or_get_client(url)
    client.send_message(message)
    client.receive_message
  end

  def open?
    !@socket.closed?
  end

  def close
    frame = WebSocket::Frame::Outgoing::Client.new(version: @handshake.version, type: :close)
    @socket.write(frame.to_s)
    @socket.close
  end

  private

  def default_port
    @uri.scheme == 'wss' ? 443 : 80
  end

  def open_socket
    tcp = TCPSocket.new(@host, @port)

    if @uri.scheme == 'wss'
      ssl_context = OpenSSL::SSL::SSLContext.new
      ssl_context.verify_mode = OpenSSL::SSL::VERIFY_NONE
      ssl = OpenSSL::SSL::SSLSocket.new(tcp, ssl_context)
      ssl.sync_close = true
      ssl.hostname = @host
      ssl.connect
      ssl
    else
      tcp
    end
  end

  def perform_handshake
    @socket.write(@handshake.to_s)

    until @handshake.finished?
      line = @socket.gets
      break if line.nil?

      @handshake << line
    end

    raise "WebSocket handshake failed!" unless @handshake.valid?
  end
end
