import functools

import grpc


class OpenOBDException(Exception):
    """
    Base class for all exceptions that can be raised when using the openobd library.
    """

    def __init__(self, details="", status=-1, status_description=""):
        self.details = details
        self.status = status
        self.status_description = status_description

    def __str__(self):
        exception_info = self.__class__.__name__

        if self.details:
            exception_info += f": {self.details}"
        if self.status != -1:
            exception_info += f" (gRPC status: {self.status}"
            if self.status_description:
                exception_info += f", {self.status_description}"
            exception_info += ")"

        return exception_info

class OpenOBDStreamException(OpenOBDException):
    """
    Exception that can occur when handling gRPC streams.
    """
    pass


class OpenOBDStreamStoppedException(OpenOBDStreamException):
    pass


class OpenOBDStreamTimeoutException(OpenOBDStreamException):
    pass



def raises_openobd_exceptions(func):
    """
    If the wrapped function raises a gRPC exception, it will be cast and raised as an OpenOBDException.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, grpc.Call):
                # Encountered an exception raised by gRPC, so cast it to an OpenOBDException
                raise OpenOBDException(details=e.details(), status=e.code().value[0], status_description=e.code().value[1]) from None
            else:
                # The exception wasn't raised by gRPC, so just raise it as is
                raise e

    return wrapper
