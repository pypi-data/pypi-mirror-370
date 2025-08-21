class KeyNotFoundError(KeyError):
    """
    Exception raised when a key is not found in the tree.

    Args:
        key (str): The key that was not found.
        message (str, optional): Additional error message. Defaults to None.
    """
    def __init__(self, key, message=None):
        if message is None:
            message = f"Key '{key}' not found in the tree."
        super().__init__(message)
        self.key = key


class InvalidSymbolsError(ValueError):
    """
    Exception raised when a string longer than one character is passed as a symbol.

    Args:
        invalid_symbols (list): The list of invalid symbols passed as keys.
        message (str, optional): Additional error message. Defaults to None.
    """
    def __init__(self, invalid_symbols, message=None):
        if message is None:
            message = (
                f"Invalid symbols in input data. "
                f"All symbols must be single-character symbols (e.g., 'a', 'b', 'c'); got: {invalid_symbols}."
            )
        super().__init__(message)
        self.invalid_symbols = invalid_symbols


class InvalidScoresError(ValueError):
    """Exception raised when invalid scores are passed as input.

    Args:
        invalid_scores (list): The list of invalid scores.
        message (str, optional): Additional error message. Defaults to None.
    """
    def __init__(self, invalid_scores, message=None):
        if message is None:
            message = (
                f"Invalid scores in input data. "
                f"All weights must be floats in the range [0, 1]; got {invalid_scores}."

            )
        super().__init__(message)
        self.invalid_scores = invalid_scores
