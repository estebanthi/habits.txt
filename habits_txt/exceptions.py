import habits_txt.directives as directives


class ParseError(Exception):
    def __init__(self, message):
        self.message = message


class ConsistencyError(Exception):
    def __init__(self, message: str, directive: directives.Directive):
        self.message = f"Consistency error in line {directive.lineno}: {message}"

    def __str__(self):
        return self.message
