"""Module for custom errors."""

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

class CannotParseRatingError(Exception):
    """Exception thrown when the user rating can't be parsed."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TooHighRatingError(Exception):
    """Exception thrown when the user submitted rating is over the defined max limit."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TooLowRatingError(Exception):
    """Exception thrown when the user submitted rating is over the defined max limit."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidStarRatingError(Exception):
    """Exception thrown when the user submitted rating is over the defined max limit."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class EmptyFootageDirectoryError(Exception):
    """Exception thrown when the user submitted rating is over the defined max limit."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TooManyMinutesWarning(Exception):
    """A non-fatal warning that warns that the obsidian note has too many minutes in playtime_mins. (Must be under 60)"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
