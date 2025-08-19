from configparser import ConfigParser

class ConfigHandler(object):

    def __init__(self, config_file, config_file_section):
        self.config_file = config_file
        self.config_file_section = config_file_section
    
    def read_config(self):
        
        # create a parser
        parser = ConfigParser()

        #read config file
        parser.read(self.config_file)

        #get config section
        config = {}
        if parser.has_section(self.config_file_section):
            params = parser.items(self.config_file_section)

            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in file {1}'.format(self.config_file_section, self.config_file))
        
        return config