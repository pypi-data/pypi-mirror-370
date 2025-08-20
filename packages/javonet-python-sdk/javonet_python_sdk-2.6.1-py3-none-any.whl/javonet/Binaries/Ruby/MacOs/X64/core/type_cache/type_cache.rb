class TypeCache
  attr_accessor :type_cache

  def self.instance
    @instance ||= new
  end

  private_class_method :new

  def initialize
    @type_cache = []
  end

  def cache_type(type_regex)
    @type_cache << type_regex
  end

  def is_type_cache_empty?
    @type_cache.empty?
  end

  def is_type_allowed(type_to_check)
    name_to_check = if type_to_check.is_a?(Module)
                      type_to_check.name
                    else
                      "#{type_to_check.class.name}::#{type_to_check.name}"
                    end

    @type_cache.any? do |pattern|
      /#{pattern}/.match?(name_to_check)
    end
  end

  def get_cached_types
    @type_cache
  end

  def clear_cache
    @type_cache.clear
    0
  end
end