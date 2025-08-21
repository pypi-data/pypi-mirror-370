class EmptyQueryError(ValueError):
    """
    Exception raised when input query is empty.

    Args:
        message (str, optional): Additional error message. Defaults to "Input query is empty."
    """
    def __init__(self, message=None):
        if message is None:
            message = "Input query is empty."
        super().__init__(message)
