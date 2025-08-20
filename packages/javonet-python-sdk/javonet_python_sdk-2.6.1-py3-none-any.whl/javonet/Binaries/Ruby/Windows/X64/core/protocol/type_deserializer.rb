require_relative '../../utils/string_encoding_mode'

class TypeDeserializer

  def self.deserialize_command(command_byte_array)
    Command.new(RuntimeName(command_byte_array[0]), CommandType(command_byte_array[1]), [])
  end

  def self.deserialize_string(string_encoding_mode, encoded_string)
    raw_str = encoded_string.map(&:chr).join
    case string_encoding_mode
    when StringEncodingMode::ASCII
      raw_str.force_encoding("US-ASCII").encode("UTF-8")
    when StringEncodingMode::UTF8
      raw_str.force_encoding("UTF-8").encode("UTF-8")
    when StringEncodingMode::UTF16
      raw_str.force_encoding("UTF-16LE").encode("UTF-8")
    when StringEncodingMode::UTF32
      raw_str.force_encoding("UTF-32").encode("UTF-8")
    else
      raise "Argument out of range in deserialize_string"
    end
  end

  def self.deserialize_int(encoded_int)
    # Assuming a 32-bit little-endian integer.
    value = 0
    encoded_int.each_with_index do |byte, index|
      value |= (byte & 0xFF) << (8 * index)
    end
    # Sign the extension if the 31st bit is set.
    value -= (1 << 32) if (value & (1 << 31)) != 0
    value
  end

  def self.deserialize_bool(encoded_bool)
    encoded_bool[0] == 1
  end

  def self.deserialize_float(encoded_float)
    # Reconstruct the 32-bit integer from the byte array.
    bits = 0
    encoded_float.each_with_index do |byte, index|
      bits |= (byte & 0xFF) << (8 * index)
    end

    # IEEE 754 single precision (32-bit) decoding:
    sign     = ((bits >> 31) == 0) ? 1 : -1
    exponent = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF

    if exponent == 255
      # Handle special cases for Inf and NaN.
      return fraction == 0 ? sign * Float::INFINITY : Float::NAN
    elsif exponent == 0
      # Subnormal numbers.
      return sign * (fraction.to_f / (1 << 23)) * (2 ** (-126))
    else
      # Normalized number.
      return sign * (1 + fraction.to_f / (1 << 23)) * (2 ** (exponent - 127))
    end
  end

  def self.deserialize_byte(encoded_byte)
    encoded_byte[0]
  end

  def self.deserialize_char(encoded_char)
    encoded_char[0].ord
  end

  def self.deserialize_longlong(encoded_long)
    # Assuming a 64-bit little-endian integer.
    value = 0
    encoded_long.each_with_index do |byte, index|
      value |= (byte & 0xFF) << (8 * index)
    end
    # Sign extension for 64-bit: if the 63rd bit is set.
    value -= (1 << 64) if value >= (1 << 63)
    value
  end

  def self.deserialize_double(encoded_double)
    # Reconstruct the 64-bit bit pattern from the byte array.
    bits = 0
    encoded_double.each_with_index do |byte, index|
      bits |= (byte & 0xFF) << (8 * index)
    end

    # IEEE 754 double precision (64-bit) decoding:
    sign     = ((bits >> 63) == 0) ? 1 : -1
    exponent = (bits >> 52) & 0x7FF
    fraction = bits & 0xFFFFFFFFFFFFF

    if exponent == 2047
      return fraction == 0 ? sign * Float::INFINITY : Float::NAN
    elsif exponent == 0
      return sign * (fraction.to_f / (1 << 52)) * (2 ** (-1022))
    else
      return sign * (1 + fraction.to_f / (1 << 52)) * (2 ** (exponent - 1023))
    end
  end

  def self.deserialize_ullong(encoded_ullong)
    # Assuming an unsigned 64-bit little-endian integer.
    value = 0
    encoded_ullong.each_with_index do |byte, index|
      value |= (byte & 0xFF) << (8 * index)
    end
    value
  end

  def self.deserialize_uint(encoded_uint)
    # Assuming an unsigned 32-bit little-endian integer.
    value = 0
    encoded_uint.each_with_index do |byte, index|
      value |= (byte & 0xFF) << (8 * index)
    end
    value
  end

  def self.deserialize_nil(encoded_nil)
    nil
  end

end
