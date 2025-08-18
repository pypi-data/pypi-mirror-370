from .error_code import ErrorCode, error_code_message_mapper


class ServiceException(Exception):
    """
    Indicates an issue when communicating with the Camunda 8 API
    """

    def __init__(self, error_code: ErrorCode = None, message: str = None, parameters=None):
        if parameters is None:
            parameters = []
        if error_code:
            self.error_code = error_code
            self.message = error_code_message_mapper(error_code, parameters)
        elif message:
            self.error_code = ErrorCode.GENERIC_ERROR
            self.message = message
        else:
            self.error_code = ErrorCode.GENERIC_ERROR
            self.message = error_code_message_mapper(self.error_code, parameters)
        super().__init__(self.message)

    def get_log_formatted_message(self):
        return f"{self.error_code.name} -> {self.message}"
