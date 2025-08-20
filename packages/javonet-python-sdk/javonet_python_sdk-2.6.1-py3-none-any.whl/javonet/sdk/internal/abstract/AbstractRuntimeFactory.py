import abc


class AbstractRuntimeFactory(abc.ABC):

    def clr(self):
        pass

    def jvm(self):
        pass

    def netcore(self):
        pass

    def perl(self):
        pass

    def ruby(self):
        pass

    def nodejs(self):
        pass

    def python(self):
        pass

    def python27(self):
        pass
