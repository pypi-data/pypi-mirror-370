from openobd_protocol.Communication.Messages.Kline_pb2 import KlineChannel, KlineMessage

from openobd.communication.response_exceptions import *
from openobd.core.session import OpenOBDSession
from openobd.communication.uds_request_handler import UdsRequestHandler
from openobd.core.stream_handler import StreamHandler


class KlineSocket:

    def __init__(self, openobd_session: OpenOBDSession, kline_channel: KlineChannel, timeout: float | None = 10):
        """
        Handles sending ISO 14230 K-Line messages to the given channel, and receiving their responses.

        :param openobd_session: an active OpenOBDSession with which to start the K-Line stream.
        :param kline_channel: the channel which to send messages to.
        :param timeout: time in seconds to wait for each response before raising a NoResponseException. None will wait forever.
        """
        self.stream_handler = StreamHandler(openobd_session.open_kline_stream, outgoing_stream=True)
        self._channel = kline_channel
        self.uds_request_handler = UdsRequestHandler(self.stream_handler, timeout)

        # Pre-emptively send a message with an empty payload to ensure the K-Line channel is set up by the server
        self.stream_handler.send(KlineMessage(channel=self._channel, payload=""))

    def request(self, payload: str, timeout: float | None = None, silent: bool = False, tries: int = 1) -> str | None:
        """
        Sends the given payload and waits for the response. Raises the appropriate ResponseException when receiving a
        negative response.

        :param payload: the bytes to send to the channel.
        :param timeout: time in seconds to wait for a response before raising a NoResponseException. Will use self.timeout if None.
        :param silent: if True, will not raise any ResponseExceptions. Instead, returns the payload of negative responses or None for NoResponseExceptions.
        :param tries: how many times to send the payload until a positive response is received.
        :return: the payload of the received response.
        """
        try:
            message = KlineMessage(channel=self._channel, payload=payload)
            return self.uds_request_handler.request(message, timeout, silent, tries)
        except ResponseException as e:
            # Add channel info to the exception before raising it
            e.request_id = self._channel.ecu_id
            raise e

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new Socket object will have to be created to start another
        stream.
        """
        self.uds_request_handler.stop_stream()
