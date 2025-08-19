class CustomError(Exception):
    """Base class for other exceptions"""
    pass


class InputError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message} - {self.errors}"


class InferenceError(Exception):
    def __init__(self, message, errors=None):
        self.message = message
        self.errors = errors
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message} - {self.errors}"
