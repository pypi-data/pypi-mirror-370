from openobd_protocol.ConnectionMonitor.Messages.ConnectorInformation_pb2 import ConnectorInformation

from openobd.core.session import OpenOBDSession
from openobd.core.stream_handler import StreamHandler

class ConnectionMonitor:

    def __init__(self, openobd_session: OpenOBDSession, sample_size: int = 10):
        """
        Starts a stream which receives a ConnectorInformation message each second. Saves the most recently received
        ConnectorInformation messages, and allows them to be returned when requested.

        :param openobd_session: an active OpenOBDSession from which to receive connection information.
        :param sample_size: the maximum amount of ConnectorInformation messages that should be saved at a time.
        """
        self.stream_handler = StreamHandler(openobd_session.open_connector_information_stream, outgoing_stream=False)
        self.sample_size = sample_size
        self._connector_info_samples = []

    def get_connector_info_list(self) -> list[ConnectorInformation]:
        """
        Returns the latest ConnectorInformation messages. The amount of returned messages is dependent on this object's
        sample_size.

        :return: a list containing the latest ConnectorInformation messages, ordered from most recent to oldest.
        """
        # Add any new ConnectorInformation messages to the self._connector_info_samples list
        connector_sample = self.stream_handler.receive(block=False)
        while connector_sample is not None:
            self._connector_info_samples.append(connector_sample)
            connector_sample = self.stream_handler.receive(block=False)

        # Make sure the list does not exceed self.sample_size, by taking only the most recent messages
        self._connector_info_samples = self._connector_info_samples[-self.sample_size:]

        # Reverse the list, so the samples are ordered latest to oldest, and return it
        return self._connector_info_samples[::-1]

    def stop_stream(self) -> None:
        """
        Closes the gRPC stream if it is not already closed. A new ConnectionMonitor object will have to be created to
        start another stream.
        """
        self.stream_handler.stop_stream()

    @staticmethod
    def print_connector_information_list(connector_information_list: list[ConnectorInformation]) -> None:
        """
        For each given ConnectorInformation message, print the info it contains.

        :param connector_information_list: a list containing the ConnectorInformation messages to be printed.
        """
        for message in connector_information_list:
            print(f" connected:         {message.connected}")
            print(f" connected since:   {message.connected_since}")
            print(f" latency:           {message.latency} ms")
            print(f" healthy:           {message.healthy}\n")
