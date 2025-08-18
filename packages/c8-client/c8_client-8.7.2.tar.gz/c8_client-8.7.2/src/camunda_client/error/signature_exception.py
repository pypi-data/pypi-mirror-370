from .service_exception import ServiceException


class WorkerSignatureException(ServiceException):
    """
    Indicates an issue with the setup of a @camunda_worker decorated function
    """

    def __str__(self):
        """
        Overrides the default string representation of the exception
        to include the error_code.
        """
        original_message = super().__str__()
        return f"{self.error_code.name} -> {original_message}"
