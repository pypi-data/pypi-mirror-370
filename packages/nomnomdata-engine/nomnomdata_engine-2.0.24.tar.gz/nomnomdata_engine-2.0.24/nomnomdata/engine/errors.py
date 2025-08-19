class ParameterError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = []

    def add_key(self, key):
        self.keys.append(key)

    def __str__(self):
        return ".".join(reversed(self.keys)) + ": " + super().__str__()


class ValidationError(ParameterError):
    pass


class MissingParameters(ValidationError):
    def __str__(self):
        return ".".join(reversed(self.keys)) + " is missing"


class LoadError(ParameterError):
    pass
