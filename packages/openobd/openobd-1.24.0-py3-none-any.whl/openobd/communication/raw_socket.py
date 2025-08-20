from openobd_protocol.Communication.Messages.Raw_pb2 import RawChannel, RawFrame

from openobd.core.session import OpenOBDSession
from openobd.core.stream_handler import StreamHandler


class RawSocket:

    def __init__(self, openobd_session: OpenOBDSession, raw_channel: RawChannel, timeout: float | None = 10):
        """
        Handles sending and receiving frame payloads to and from the given channel.

        :param openobd_session: an active OpenOBDSession with which to start the raw frames stream.
        :param raw_channel: the channel which to exchange frames with.
        :param timeout: time in seconds to wait for an incoming frame before raising a OpenOBDStreamTimeoutException. None will wait forever.
        """
        self.stream_handler = StreamHandler(openobd_session.open_raw_stream, outgoing_stream=True)
        self._channel = raw_channel
        self.timeout = timeout
        '''We send an empty message to the server to ensure that the channel is initialized, this also helps when we 
        want to just listen on a channel'''
        self.stream_handler.send(RawFrame(channel=self._channel, payload=""))

    def send(self, payload: str, flush_incoming_messages: bool = False) -> None:
        """
        Sends the given payload to the channel.

        :param payload: the payload of the frame to send to the channel.
        :param flush_incoming_messages: discards all currently pending incoming frames before sending the payload.
        """
        message = RawFrame(channel=self._channel, payload=payload)
        self.stream_handler.send(message, flush_incoming_messages)

    def receive(self, block: bool = True, timeout: float | None = None) -> str | None:
        """
        Retrieves the oldest pending incoming frame. If there are no pending frames, wait until a new frame arrives.

        :param block: whether to wait for a new frame if there are no pending frames. If False, returns None when no frames are pending.
        :param timeout: time in seconds to wait for a new frame before raising a OpenOBDStreamTimeoutException. Will use self.timeout if None.
        :return: the payload received from the channel.
        """
        timeout = timeout if timeout is not None else self.timeout
        response = self.stream_handler.receive(block, timeout)
        if response is not None:
            return response.payload.upper()

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new RawSocket object will have to be created to start
        another stream.
        """
        self.stream_handler.stop_stream()
