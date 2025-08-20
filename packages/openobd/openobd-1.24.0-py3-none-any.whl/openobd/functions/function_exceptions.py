from openobd_protocol.Function.Messages.Function_pb2 import FunctionContext
from openobd_protocol.Session.Messages.ServiceResult_pb2 import Result, UserFeedback

from openobd.core.exceptions import OpenOBDException


class OpenOBDFunctionException(OpenOBDException):
    """
    Base class for all exceptions that can be raised when running functions.
    """

    def __init__(self, function_id: str = None, function_context: FunctionContext = None, **kwargs):
        self.function_id = function_id
        self.function_context = function_context
        super().__init__(**kwargs)

    def __str__(self):
        exception_data = []

        if self.function_id:
            exception_data.append(f"Function ID [{self.function_id}].")

        if self.function_context:
            if self.function_context.service_result.result:
                results = []
                for result in self.function_context.service_result.result:
                    results.append(Result.Name(result))
                results_string = ", ".join(results)
                exception_data.append(f"Result(s): {results_string}.")
            else:
                exception_data.append("No result set.")

            if self.function_context.service_result.user_feedback:
                exception_data.append(f"User feedback: {UserFeedback.Name(self.function_context.service_result.user_feedback)}.")

        exception_string = self.__class__.__name__
        if len(exception_data) != 0:
            exception_string += ": " + " ".join(exception_data)

        return exception_string


class OpenOBDFunctionUnsuccessfulException(OpenOBDFunctionException):
    """
    The result of the function is not only set to success.
    """
    pass


class OpenOBDFunctionDeadlineExceededException(OpenOBDFunctionException):
    """
    The requested function did not respond in time.
    """
    pass


class OpenOBDFunctionPermissionDeniedException(OpenOBDFunctionException):
    """
    You are not allowed to execute the requested function.
    """
    pass


class OpenOBDFunctionUnavailableException(OpenOBDFunctionException):
    """
    The requested function is not available.
    """
    pass
