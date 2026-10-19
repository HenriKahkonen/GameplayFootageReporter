class EnvReadError(Exception):
    """Exception raised for when reading from .env file fails."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidPathError(Exception):
    """Exception raised when user submitted path is invalid."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidArgumentError(Exception):
    """Exception raised when user submitted argument is invalid."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MalformedSettingsError(Exception):
    """Exception raised when the settings.py file is malformed and expected values can't be read from it."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)