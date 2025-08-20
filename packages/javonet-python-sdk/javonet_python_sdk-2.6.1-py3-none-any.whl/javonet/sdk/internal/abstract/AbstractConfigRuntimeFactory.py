import abc


class AbstractConfigRuntimeFactory(abc.ABC):

    def clr(self, config_name: str = "default"):
        pass

    def jvm(self, config_name: str = "default"):
        pass

    def netcore(self, config_name: str = "default"):
        pass

    def perl(self, config_name: str = "default"):
        pass

    def ruby(self, config_name: str = "default"):
        pass

    def nodejs(self, config_name: str = "default"):
        pass

    def python(self, config_name: str = "default"):
        pass

    def python27(self, config_name: str = "default"):
        pass