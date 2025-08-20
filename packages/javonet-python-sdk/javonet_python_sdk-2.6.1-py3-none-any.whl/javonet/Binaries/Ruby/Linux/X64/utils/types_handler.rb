class TypesHandler
  def self.primitive_or_none?(item)
    item.is_a?(Integer) ||
      item.is_a?(Float) ||
      item.is_a?(TrueClass) ||
      item.is_a?(FalseClass) ||
      item.is_a?(String) ||
      item.nil?
  end
end
