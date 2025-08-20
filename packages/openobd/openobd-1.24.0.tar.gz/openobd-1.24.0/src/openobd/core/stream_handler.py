import functools
import threading
import typing
from queue import Queue, Empty
from collections.abc import Callable, Iterator, Iterable
from typing import Any
from grpc import Call, StatusCode
from openobd_protocol.Messages import Empty_pb2 as grpcEmpty

from openobd.core.exceptions import OpenOBDException, OpenOBDStreamException, OpenOBDStreamStoppedException, OpenOBDStreamTimeoutException

class IteratorStopped(Exception):
    pass

def requires_active_iterator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        iterator = args[0]
        assert isinstance(iterator, MessageIterator), "Decorator 'requires_active_iterator' used outside of MessageIterator!"
        if not iterator.is_active:
            raise IteratorStopped("Unable to fulfill request, as the iterator has been stopped.")
        return func(*args, **kwargs)
    return wrapper


class MessageIterator:

    def __init__(self, message: Any = None):
        self.is_active = True

        self._next_messages = Queue()
        self._lock = threading.RLock()
        self._next_iteration_condition = threading.Condition(self._lock)
        self._queue_empty_condition = threading.Condition(self._lock)
        self._stopped_iteration_condition = threading.Condition(self._lock)
        if message is not None:
            self.send_message(message)

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            if not self.is_active:
                self._stopped_iteration_condition.notify_all()
                raise StopIteration

            if self._next_messages.qsize() == 0:
                self._queue_empty_condition.notify_all()
                self._next_iteration_condition.wait()
                if not self.is_active:
                    self._stopped_iteration_condition.notify_all()
                    raise StopIteration

            value = self._next_messages.get()
        return value

    @requires_active_iterator
    def send_message(self, message: Any):
        with self._lock:
            self._next_messages.put(message)
            self._next_iteration_condition.notify_all()

    @requires_active_iterator
    def stop(self, send_remaining_messages=False):
        with self._lock:
            if send_remaining_messages:
                self.wait_until_messages_sent()
            self.is_active = False
            self._next_iteration_condition.notify_all()
            # Wait until the iterator has raised a StopIteration exception before returning
            self._stopped_iteration_condition.wait(1)

    @requires_active_iterator
    def wait_until_messages_sent(self, timeout=10):
        with self._lock:
            if self._next_messages.qsize() == 0:
                return
            self._queue_empty_condition.wait(timeout)


class ThreadSafeVariable:

    def __init__(self, value=None):
        self._value = value
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, value):
        with self._lock:
            self._value = value


class StreamState:
    UNDEFINED = 0
    ACTIVE = 1
    SHUTTING_DOWN = 2   # The stream has received a cancel signal and cannot send messages anymore, but might still receive any final incoming messages
    CLOSED = 3


def requires_active_stream(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        stream_handler = args[0]
        assert isinstance(stream_handler, StreamHandler), "Decorator 'requires_active_stream' used outside of a StreamHandler class!"
        if stream_handler.received_exception:
            raise stream_handler.received_exception
        if stream_handler.stream_state != StreamState.ACTIVE:
            raise OpenOBDStreamStoppedException("Unable to fulfill request, as there is no stream active.")
        return func(*args, **kwargs)
    return wrapper


class StreamHandler:

    def __init__(self, stream_function: Callable[[Any], Any], request: Any = None, **kwargs):
        """
        Allows easier handling of a gRPC stream by providing methods to send and receive messages.

        :param stream_function: a reference to the function which should be used to send and receive messages.
        :param request: the message to send when not using an outgoing stream. Leave it None to send an EmptyMessage.

        :keyword outgoing_stream: boolean specifying whether the function requires a stream of messages as input. If not given, tries to detect it based on the function's type hints.
        """
        # Explicitly set whether an outgoing stream is used (if given as kwarg), or detect it based on type hints
        outgoing_stream = kwargs["outgoing_stream"] if "outgoing_stream" in kwargs else self._has_outgoing_stream(stream_function)
        assert isinstance(outgoing_stream, bool), "kwarg outgoing_stream must be a boolean."

        # self._request_iterator is only required for outgoing streams
        self._request_iterator = MessageIterator() if outgoing_stream else None

        # Determine the request that should be passed when starting the stream
        if outgoing_stream:
            request = self._request_iterator
        else:
            request = request if request is not None else grpcEmpty.EmptyMessage()

        # Set up required attributes (use ThreadSafeVariables for some to help prevent race conditions)
        self.__response_iterator = ThreadSafeVariable(None)     # Represents the incoming stream
        self._incoming_messages = Queue()    # Stores all incoming messages to later be retrieved
        self._stream_state = ThreadSafeVariable(StreamState.ACTIVE)
        self.received_exception = None

        # Start the thread containing the stream
        stream_thread = threading.Thread(target=self._stream, args=[stream_function, request], daemon=True)
        stream_thread.start()

    @property
    def _response_iterator(self):
        return self.__response_iterator.value

    @_response_iterator.setter
    def _response_iterator(self, value):
        self.__response_iterator.value = value

    @property
    def stream_state(self):
        return self._stream_state.value

    @stream_state.setter
    def stream_state(self, value):
        self._stream_state.value = value

    @staticmethod
    def _has_outgoing_stream(function: Callable[[Any], Any]) -> bool:
        type_hints = typing.get_type_hints(function)
        parameters = {k: v for k, v in type_hints.items() if k != "return"}
        parameter_type = next(iter(parameters.values()), None)
        # Check if any type hints were found before returning
        if parameter_type is None:
            raise OpenOBDStreamException("Unable to detect whether the given stream function requires an outgoing stream. Please pass it explicitly using the outgoing_stream kwarg.")
        return typing.get_origin(parameter_type) == Iterator

    def _get_incoming_message(self, block: bool = True, timeout: float | None = None) -> Any:
        try:
            incoming_message = self._incoming_messages.get(block=block, timeout=timeout)
            # If an exception occurred while waiting, raise it
            if isinstance(incoming_message, Exception):
                raise incoming_message
            else:
                return incoming_message
        except Empty:
            if block:
                raise OpenOBDStreamTimeoutException from None
            else:
                return None

    def receive(self, block: bool = True, timeout: float | None = None) -> Any:
        """
        Retrieves the oldest pending message. If there are no pending messages, wait until a new message arrives.
        Raises an OpenOBDStreamStoppedException if the stream is closed and there are no more pending messages.

        :param block: whether to wait for a new message if there are no pending messages. If False, returns None when no messages are pending.
        :param timeout: time in seconds to wait for a new message before raising an OpenOBDStreamTimeoutException. None will wait forever.
        :return: a message received by the gRPC stream.
        """
        # If an exception occurred in this stream, raise it
        if self.received_exception:
            raise self.received_exception

        # Check if there are currently any pending messages to receive (without spending any time waiting/blocking)
        incoming_message = self._get_incoming_message(block=False)
        if incoming_message is not None:
            return incoming_message

        if self.stream_state == StreamState.CLOSED:
            # All messages have been received and the stream is closed
            raise OpenOBDStreamStoppedException("The stream has been closed, so no further messages can be received.")

        # There are no pending messages, and the stream is still active, so wait for an incoming message as specified by the arguments
        return self._get_incoming_message(block=block, timeout=timeout)

    def flush_incoming_messages(self):
        """
        Discards all currently pending incoming messages.
        """
        with self._incoming_messages.mutex:
            self._incoming_messages.queue.clear()

    @requires_active_stream
    def send(self, message: Any, flush_incoming_messages: bool = False) -> None:
        """
        Sends a new message on this object's stream.

        :param message: the message to send on the stream.
        :param flush_incoming_messages: discards all currently pending incoming messages before sending the message.
        """
        if self._request_iterator is None:
            raise OpenOBDStreamException("It is not possible to send messages, as this object does not have an outgoing stream.")

        if flush_incoming_messages:
            self.flush_incoming_messages()

        self._request_iterator.send_message(message)

    @requires_active_stream
    def send_and_close(self, messages: Iterable, block: bool = True, timeout: float | None = None) -> Any:
        """
        Sends all the given messages on the stream, stops the stream after sending them, and returns the received
        response. This method is meant for calls that have an outgoing stream, and receive a single, unary response.

        :param messages: an iterable containing each message that should be sent on the stream.
        :param block: whether to wait for the response if there are no pending messages. If False, returns None when no messages are pending.
        :param timeout: time in seconds to wait for the response before raising an OpenOBDStreamTimeoutException. None will wait forever.
        :return: the response received from the gRPC stream.
        """
        if self._request_iterator is None:
            raise OpenOBDStreamException("It is not possible to send messages, as this object does not have an outgoing stream.")

        for message in messages:
            self.send(message)
        self.stop_stream(send_remaining_messages=True)
        return self.receive(block=block, timeout=timeout)

    def stop_stream(self, send_remaining_messages: bool = True) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new StreamHandler object will have to be created to start
        another stream.
        
        :param send_remaining_messages: whether to wait for all outgoing messages to be sent before stopping the stream.
        """
        # Indicate the stream is shutting down to prevent attempts at sending messages immediately after this call
        self.stream_state = StreamState.SHUTTING_DOWN

        if self._request_iterator is not None:
            # Stops the outgoing stream
            if self._request_iterator.is_active:
                self._request_iterator.stop(send_remaining_messages=send_remaining_messages)

        if self._response_iterator is not None:
            # Stops the incoming stream. If cancel is not present, it's fine
            if hasattr(self._response_iterator, "cancel"):   # Method defined by gRPC. Should always be present (sanity check).
                self._response_iterator.cancel()

    def _stream(self, stream_function: Callable[[Any], Any], request: Any) -> None:
        """
        Places any incoming messages in self._incoming_messages as they arrive.
        """
        try:
            # Start the stream by passing the request to the stream function
            response = stream_function(request)
            if isinstance(response, Iterator):
                # The server returned an iterator, which means that there is an incoming stream
                self._response_iterator = response
                # Check if the stream received a stop signal before it even started
                if self.stream_state != StreamState.ACTIVE:
                    self.stop_stream()
                # Handle the incoming stream
                for message in self._response_iterator:
                    self._incoming_messages.put(message)
            else:
                # There's no incoming stream, so merely pass on the response
                self._incoming_messages.put(response)
        except Exception as e:
            if (isinstance(e, Call) and e.code() == StatusCode.CANCELLED) or \
                    (isinstance(e, OpenOBDException) and e.status == 1):
                # The stream has been cancelled, so there's no need to stop it again or raise an exception
                pass
            else:
                self.stop_stream()

                if isinstance(e, Call):
                    # Encountered an exception raised by gRPC, so cast it to an OpenOBDStreamException
                    grpc_exception = OpenOBDStreamException(details=e.details(), status=e.code().value[0], status_description=e.code().value[1])
                    self.received_exception = grpc_exception
                else:
                    self.received_exception = e

                # In case receive() is currently waiting for an incoming message, pass them the exception
                self._incoming_messages.put(self.received_exception)
        finally:
            self.stream_state = StreamState.CLOSED

            # Put a StreamStoppedException in the queue to indicate to any blocking receive() calls that the stream has ended
            self._incoming_messages.put(OpenOBDStreamStoppedException("The stream has been closed, so no further messages can be received."))
