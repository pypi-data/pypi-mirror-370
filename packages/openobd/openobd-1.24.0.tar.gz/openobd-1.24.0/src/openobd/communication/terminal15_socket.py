from openobd_protocol.Communication.Messages import Terminal15_pb2 as grpcTerminal15

from openobd.core.session import OpenOBDSession
from openobd.core.stream_handler import StreamHandler

class Terminal15Socket:

    def __init__(self, openobd_session: OpenOBDSession, timeout: float | None = 10):
        """
        Handles receiving terminal15 signals from the given channel.

        :param openobd_session: an active OpenOBDSession with which to start the stream.
        :param timeout: time in seconds to wait for an incoming frame before raising a OpenOBDStreamTimeoutException. None will wait forever.
        """
        self.stream_handler = StreamHandler(openobd_session.open_terminal15_stream, outgoing_stream=False)
        self.timeout = timeout

    def receive(self, block: bool = True, timeout: float | None = None) -> str | None:
        """
        Retrieves the oldest pending incoming message. If there are no pending messages, wait until a new message arrives.

        :param block: whether to wait for a new message if there are no pending messages. If False, returns None when no messages are pending.
        :param timeout: time in seconds to wait for a new frame before raising a OpenOBDStreamTimeoutException. Will use self.timeout if None.
        :return: the payload received from the channel.
        """
        timeout = timeout if timeout is not None else self.timeout
        response = self.stream_handler.receive(block, timeout)
        if response is not None:
            if response.state == grpcTerminal15.STATE_ON:
                return "ON"
            elif response.state == grpcTerminal15.STATE_OFF:
                return "OFF"
            else:
                return "UNDEFINED"

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new RawSocket object will have to be created to start
        another stream.
        """
        self.stream_handler.stop_stream()
