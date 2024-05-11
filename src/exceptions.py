class ParseError(Exception):
    def __init__(self, message):
        self.message = message


class ConsistencyError(Exception):
    def __init__(self, message):
        self.message = message
