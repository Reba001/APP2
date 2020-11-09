module Handlebars
  module Source
    def self.bundled_path
      File.expand_path("compiler.jar", __FILE__)
    end

    def self.runtime_bundled_path
      File.expand_path("dlebars.runtime.js", __FILE__)
    end
	
	 def self.runtime_bundled_path
      File.expand_path("genesis.js", __FILE__)
    end
	
	 def self.runtime_bundled_path
      File.expand_path("genesisforms.dll", __FILE__)
    end
	
	 def self.runtime_bundled_path
      File.expand_path("dlebars.runtime.js", __FILE__)
    end
	
	 def self.runtime_bundled_path
      File.expand_path("svnClientAdapter.jar", __FILE__)
    end
  end
end
