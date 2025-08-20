class ReferencesCache
  # Make 'new' a private class method so no other instances can be created.
  private_class_method :new

  def self.instance
    @instance ||= new
  end

  def initialize
    @references_cache = {}
  end

  def cache_reference(object_reference)
    uuid_ = generate_uuid
    @references_cache[uuid_] = object_reference
    uuid_
  end

  def resolve_reference(guid)
    if @references_cache[guid].nil?
      raise "Unable to resolve reference with id: #{guid}"
    else
      @references_cache[guid]
    end
  end

  def delete_reference(guid)
    if @references_cache[guid].nil?
      raise 'Object not found in reference cache'
    else
      @references_cache.delete(guid)
      0
    end
  end

  def generate_uuid
    [8, 4, 4, 4, 12].map { |n| rand(16**n).to_s(16).rjust(n, '0') }.join('-')
  end
end
