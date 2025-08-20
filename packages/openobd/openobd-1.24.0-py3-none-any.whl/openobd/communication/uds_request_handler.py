import time

from google.protobuf.message import Message

from openobd.communication.response_exceptions import *
from openobd.core.exceptions import OpenOBDStreamTimeoutException
from openobd.core.stream_handler import StreamHandler


class UdsRequestHandler:

    def __init__(self, stream_handler: StreamHandler, timeout: float | None):
        """
        A class that takes care of parsing and handling incoming UDS messages.

        :param stream_handler: a StreamHandler object that manages the stream over which to send messages.
        :param timeout: time in seconds to wait for each response before raising a NoResponseException. None will wait forever.
        """
        self.stream_handler = stream_handler
        self.timeout = timeout

    def request(self, message: Message, timeout: float | None = None, silent: bool = False, tries: int = 1) -> str | None:
        """
        Sends the given message and waits for the response. Raises the appropriate ResponseException when receiving a
        negative response.

        :param message: the gRPC message to send to the channel.
        :param timeout: time in seconds to wait for a response before raising a NoResponseException. Will use self.timeout if None.
        :param silent: if True, will not raise any ResponseExceptions. Instead, returns the payload of negative responses or None for NoResponseExceptions.
        :param tries: how many times to send the message until a positive response is received.
        :return: the payload of the received response.
        """
        assert tries > 0, "Optional argument 'tries' must be greater than zero."

        if hasattr(message, "payload"):
            payload = message.payload
        else:
            raise AttributeError("The given gRPC message must have a 'payload' attribute.")
        timeout = timeout if timeout is not None else self.timeout

        for current_try in range(1, tries + 1):
            self.stream_handler.send(message, flush_incoming_messages=True)

            try:
                end_time = time.time() + timeout if timeout is not None else None
                try:
                    return self._receive_and_handle_response(payload, timeout)
                except BusyRepeatRequestException as e:
                    # We should retry the request after waiting a little
                    if end_time is not None and time.time() + 0.5 > end_time:
                        # We don't have enough time left this try, so raise the received exception
                        raise e
                    time.sleep(0.5)
                    try:
                        # Make another request in the time we have left
                        remaining_time = max(0.0, end_time - time.time()) if end_time is not None else None
                        return self.request(message, timeout=remaining_time)
                    except NoResponseException:
                        # We did not receive another response in time, so raise the exception received earlier
                        raise e

            except ResponseException as e:
                if current_try < tries:
                    continue
                if silent:
                    return e.response
                raise e

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new object will have to be created to start another
        stream.
        """
        self.stream_handler.stop_stream()

    def _receive_and_handle_response(self, request_payload: str, timeout: float | None) -> str:
        end_time = time.time() + timeout if timeout is not None else None

        try:
            response = self.stream_handler.receive(timeout=timeout)
        except OpenOBDStreamTimeoutException:
            no_response_exc = NoResponseException(request=request_payload, response=None)
            raise no_response_exc

        response_payload = response.payload.upper()

        try:
            self._check_response_format(response_payload)

            if not self._response_matches_request(response_payload, request_payload):
                # The received message is not a response to our request, so continue listening in the time we have left
                remaining_time = max(0.0, end_time - time.time()) if end_time is not None else None
                return self._receive_and_handle_response(request_payload, remaining_time)

            try:
                self._check_response_payload(response_payload)
            except RequestCorrectlyReceivedResponsePendingException as e:
                try:
                    # We need to wait a little longer for the response, so continue listening in the time we have left
                    remaining_time = max(0.0, end_time - time.time()) if end_time is not None else None
                    return self._receive_and_handle_response(request_payload, remaining_time)
                except NoResponseException:
                    # Did not receive a timely response, so raise the original ResponsePending exception
                    raise e

        except ResponseException as e:
            # Add the request and response metadata to the exception before raising it
            e.request = request_payload
            # Only set the response attribute if it doesn't already contain a value
            if not e.response:
                e.response = response_payload
            raise e

        return response_payload

    @staticmethod
    def _check_response_format(response: str) -> None:
        """
        Checks whether the response is formatted correctly. If not, raises an InvalidResponseException.

        :param response: the payload of the response.
        """
        if response[:2] == "7F" and len(response) != 6:
            # The response does not have the correct length for a negative response
            raise InvalidResponseException()

    @staticmethod
    def _response_matches_request(response: str, request: str) -> bool:
        """
        Checks whether the service of the response matches the service of the request.

        :param response: the payload of the response.
        :param request: the payload of the request.
        :return: True if the response matches the request. False if there's a mismatch.
        """
        if response == "":
            return False

        try:
            service_byte = int(request[:2], 16)
            if response[:2] == "7F":
                if int(response[2:4], 16) != service_byte:
                    return False
            elif int(response[:2], 16) != (service_byte + 0x40):
                return False
            return True

        except ValueError:
            raise InvalidResponseException()

    @staticmethod
    def _check_response_payload(payload: str) -> None:
        """
        Checks whether the given response is a negative response. If so, raises the appropriate exception.

        :param payload: the payload of the response.
        """
        if payload[:2] != "7F":
            return
        negative_response_code = payload[4:6]
        exception = negative_response_code_exceptions.get(negative_response_code, UnknownNegativeResponseException)
        raise exception
