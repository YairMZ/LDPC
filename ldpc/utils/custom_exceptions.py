class NonBinaryMatrix(Exception):
    """Raised when a non-binary matrix is used while a binary one expected"""
    pass


class IncorrectLength(ValueError):
    """Raised when a sequence of unexpected length is sent to function"""
    pass
