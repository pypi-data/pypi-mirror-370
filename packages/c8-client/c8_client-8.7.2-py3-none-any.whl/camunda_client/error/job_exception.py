class CamundaBusinessException(Exception):
    """
    Indicates that a business error occurred while a Camunda job is processed. Should be thrown by @camunda_worker
    decorated functions.
    """

    def __init__(self, error_code: str, error_message: str, variables: dict = None):
        if variables is None:
            self.variables = {}
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self):
        return f"{self.error_code} -> {self.error_message}"
