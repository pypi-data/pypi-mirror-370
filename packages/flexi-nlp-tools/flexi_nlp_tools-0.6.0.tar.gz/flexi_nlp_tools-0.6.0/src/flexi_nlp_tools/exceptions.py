class InvalidEnvironmentVariable(ValueError):
    """
    Exception raised when an environment variable has an invalid value.

    Args:
        variable_name (str): The name of the environment variable.
        variable_value (any): The invalid value of the environment variable.
        expected_type (str): Description of the expected type or constraints.
        message (str, optional): Additional error message. Defaults to None.
    """
    def __init__(self, variable_name, variable_value, expected_type, message=None):
        if message is None:
            message = (
                f"Invalid environment variable '{variable_name}': {variable_value}. "
                f"Expected: {expected_type}."
            )
        super().__init__(message)
        self.variable_name = variable_name
        self.variable_value = variable_value
        self.expected_type = expected_type
