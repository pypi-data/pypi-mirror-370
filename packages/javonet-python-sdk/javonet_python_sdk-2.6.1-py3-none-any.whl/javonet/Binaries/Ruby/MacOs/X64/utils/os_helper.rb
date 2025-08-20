class OSHelper
  def self.windows?
    RbConfig::CONFIG['host_os'] =~ /mswin|mingw|cygwin/i
  end

  def self.mac?
    RbConfig::CONFIG['host_os'] =~ /darwin/i
  end

  def self.linux?
    RbConfig::CONFIG['host_os'] =~ /linux/i
  end

  def self.unix?
    RbConfig::CONFIG['host_os'] =~ /unix/i
  end

  def self.os_name
    RbConfig::CONFIG['host_os']
  end
end
