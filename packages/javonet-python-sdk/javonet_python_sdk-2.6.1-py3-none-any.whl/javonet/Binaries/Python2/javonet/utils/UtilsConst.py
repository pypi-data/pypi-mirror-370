import os

class UtilsConst:
    _javonet_working_directory = os.path.abspath(os.getcwd()) + "/"
    _config_source = ""
    _license_key = "License key not set"

    @staticmethod
    def set_javonet_working_directory(path):
        path = path.replace("\\", "/")
        if not path.endswith("/"):
            path = path + "/"
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(path, 0o700)
        UtilsConst._javonet_working_directory = path

    @staticmethod
    def get_javonet_working_directory():
        return UtilsConst._javonet_working_directory

    @staticmethod
    def set_config_source(value):
        UtilsConst._config_source = value

    @staticmethod
    def get_config_source():
        return UtilsConst._config_source

    @staticmethod
    def set_license_key(value):
        if not value or value == "" or value == "your-license-key":
            return
        UtilsConst._license_key = value

    @staticmethod
    def get_license_key():
        return UtilsConst._license_key