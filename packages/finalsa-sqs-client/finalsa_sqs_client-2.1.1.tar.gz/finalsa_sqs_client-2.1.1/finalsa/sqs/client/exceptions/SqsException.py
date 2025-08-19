class SqsException(Exception):

    def __init__(self, exception, message):
        self.__cause__ = exception
        self.message = message
