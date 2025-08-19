class CustomError(Exception):
    """Base class for custom exceptions in the AST module."""
    pass


class ASTError(CustomError):    
    """Exception raised for errors in the Abstract Syntax Tree operations."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"ASTError: {self.message}"