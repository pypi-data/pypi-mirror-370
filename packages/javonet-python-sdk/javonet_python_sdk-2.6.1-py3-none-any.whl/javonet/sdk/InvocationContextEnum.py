class InvocationContextEnum:

    def __init__(self, array_as_invocation_context):
        self.__array_as_invocation_context = array_as_invocation_context
        self.__position = -1

        self.__array_size = self.__array_as_invocation_context.get_size().execute().get_value()
        self.__array_as_list = [None] * self.__array_size
        for i in range(self.__array_size):
            self.__array_as_list[i] = self.__array_as_invocation_context.get_index(i)

    def __iter__(self):
        return self.__array_as_list.__iter__()

    def __next__(self):
        self.__position = self.__position + 1

    def __getitem__(self, key):
        return self.__array_as_invocation_context.get_index(key)

    def __setitem__(self, key, value):
        return self.__array_as_invocation_context.set_index(key, value).execute()
