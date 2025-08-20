from enum import Enum
from typing import Iterator

from openobd_protocol.Communication.Messages import Isotp_pb2 as grpcIsotp, Tp20_pb2 as grpcTp20, Raw_pb2 as grpcRaw, Kline_pb2 as grpcKline, \
    Terminal15_pb2 as grpcTerminal15, Doip_pb2 as grpcDoip
from openobd_protocol.Configuration.Messages import BusConfiguration_pb2 as grpcBusConfiguration
from openobd_protocol.Configuration.Messages import Configuration_pb2 as grpcConfiguration
from openobd_protocol.ConnectionMonitor.Messages import ConnectorInformation_pb2 as grpcConnectionInformation
from openobd_protocol.Function.Messages import Function_pb2 as grpcFunction
from openobd_protocol.Function.Messages.Function_pb2 import Variable
from openobd_protocol.Messages import Empty_pb2 as grpcEmpty
from openobd_protocol.Messages.Empty_pb2 import EmptyMessage
from openobd_protocol.Session.Messages import Session_pb2 as grpcSession, ServiceResult_pb2 as grpcServiceResult
from openobd_protocol.SessionController.Messages import SessionController_pb2 as grpcSessionController
from openobd_protocol.UserInterface.Messages import UserInterface_pb2 as grpcUserInterface
from openobd_protocol.VehicleInfo.Messages import VehicleInfo_pb2 as grpcVehicleInfo

from openobd.core.exceptions import raises_openobd_exceptions
from openobd.core.grpc_factory import GrpcFactory, NetworkGrpcFactory


class ContextVariableType(Enum):
    FUNCTION = 1
    GLOBAL = 2
    CONNECTION = 3

class OpenOBDSession:

    AUTH_TOKEN      = 1
    MONITOR_TOKEN   = 2
    SESSION_TOKEN   = 3

    def __init__(self, session_info: grpcSessionController.SessionInfo, grpc_port=443, grpc_factory: GrpcFactory = None):
        """
        An object that represents an openOBD session. Can be used to make session-specific gRPC calls.

        :param session_info: a SessionInfo object received from a gRPC call.
        :param grpc_port: the default value of 443 should be used to make gRPC calls using SSL.
        :param grpc_factory: GrpcFactory implementation that delegates grpc calls to the desired implementation. Defaults
                             to the NetworkGrpcFactory, which will make grpc calls to the server, specified in the session_info object.
        """
        self.active = True
        self.session_info = session_info

        '''Initially the session context is not initialized (will be initialized when starting a new context)'''
        self.function_context = None    # type: grpcFunction.FunctionContext | None

        '''Initially the session token is the authentication token for the session'''
        self.session_token = self.session_info.authentication_token

        '''Initialize a grpc channel based on the information provided, if no channel is given'''
        if grpc_factory is None:
            grpc_factory = NetworkGrpcFactory(self.session_info.grpc_endpoint, grpc_port)

        self.session = grpc_factory.get_session()
        self.function = grpc_factory.get_function()
        self.config = grpc_factory.get_config()
        self.can = grpc_factory.get_can()
        self.kline = grpc_factory.get_kline()
        self.terminal15 = grpc_factory.get_terminal15()
        self.doip = grpc_factory.get_doip()
        self.ui = grpc_factory.get_ui()
        self.connector_monitor = grpc_factory.get_connection_monitor()
        self.vehicle_info = grpc_factory.get_vehicle_info()

    def id(self):
        return self.session_info.id

    def _metadata(self, token=AUTH_TOKEN):
        bearer_token = ""
        if token == self.AUTH_TOKEN:
            bearer_token = self.session_token
        elif token == self.MONITOR_TOKEN:
            if self.function_context is not None:
                bearer_token = self.function_context.monitor_token
        elif token == self.SESSION_TOKEN:
            bearer_token = self.session_token

        '''Construct the metadata for the gRPC call'''
        metadata = []
        metadata.append(("authorization", "Bearer {}".format(bearer_token)))
        metadata = tuple(metadata)
        return metadata

    def update_session_token(self, session_token):
        """
        Replaces the session token used for gRPC calls.

        :param session_token: the new session token to use.
        """
        self.session_token = session_token

    @raises_openobd_exceptions
    def configure_bus(self, bus_configurations: Iterator[grpcBusConfiguration.BusConfiguration]) -> grpcEmpty.EmptyMessage:
        """
        Configures all given buses so that they can be used for communication. Overwrites any previous bus
        configurations.

        :param bus_configurations: BusConfiguration messages representing the buses that need to be configured.
        :return: an EmptyMessage, indicating that no problems occurred.
        """
        return self.config.configureBus(bus_configurations, metadata=self._metadata())

    @raises_openobd_exceptions
    def get_configuration(self) -> grpcConfiguration.Configuration:
        """
        Returns information on all currently configured buses and channels

        :return: an EmptyMessage, indicating that no problems occurred.
        """
        return self.config.getConfiguration(EmptyMessage(), metadata=self._metadata())

    @raises_openobd_exceptions
    def open_isotp_stream(self, isotp_messages: Iterator[grpcIsotp.IsotpMessage]) -> Iterator[grpcIsotp.IsotpMessage]:
        """
        Opens a bidirectional stream for ISO-TP communication with the channel specified in the given IsotpMessage.

        :param isotp_messages: each IsotpMessage that should be sent to the specified channel.
        :return: IsotpMessages sent by the specified channel.
        """
        return self.can.openIsotpStream(isotp_messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_tp20_stream(self, messages: Iterator[grpcTp20.Tp20Message]) -> Iterator[grpcTp20.Tp20Message]:
        """
        Opens a bidirectional stream for TP2.0 communication with the channel specified in the given Tp20Message.

        :param messages: each TP2.0 mesage that should be sent to the specified channel.
        :return: messages received on the specified channel.
        """
        return self.can.openTp20Stream(messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_raw_stream(self, raw_frames: Iterator[grpcRaw.RawFrame]) -> Iterator[grpcRaw.RawFrame]:
        """
        Opens a bidirectional stream for raw frame communication with the channel specified in the given RawFrame.

        :param raw_frames: each RawFrame that should be sent to the specified channel.
        :return: RawFrames sent by the specified channel.
        """
        return self.can.openRawStream(raw_frames, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_kline_stream(self, kline_messages: Iterator[grpcKline.KlineMessage]) -> Iterator[grpcKline.KlineMessage]:
        """
        Opens a bidirectional stream for K-Line communication with the channel specified in the given KlineMessage.

        :param kline_messages: each KlineMessage that should be sent to the specified channel.
        :return: KlineMessages sent by the specified channel.
        """
        return self.kline.openKlineStream(kline_messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_terminal15_stream(self, empty_message: EmptyMessage) -> Iterator[grpcTerminal15.Terminal15Message]:
        """
        Opens a stream for Terminal15 communication.

        :return: Terminal15 messages sent by the remote.
        """
        return self.terminal15.openTerminal15Stream(empty_message, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_doip_stream(self, doip_messages: Iterator[grpcDoip.DoipMessage]) -> Iterator[grpcDoip.DoipMessage]:
        """
        Opens a bidirectional stream for DoIP communication with the channel specified in the given DoipMessage.

        :param doip_messages: each DoipMessage that should be sent to the specified channel.
        :return: DoipMessages sent by the specified channel.
        """
        return self.doip.openDoipStream(doip_messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_control_stream(self, user_interface_messages: Iterator[grpcUserInterface.Control]) -> Iterator[grpcUserInterface.Control]:
        """
        Opens a stream that displays given Control messages to the customer or operator, and returns their response.

        :param user_interface_messages: Control messages that need to be displayed on the user interface.
        :return: Control messages containing the user's response, depending on which Control type was sent.
        """
        return self.ui.openControlStream(user_interface_messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def get_connector_information(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcConnectionInformation.ConnectorInformation:
        """
        Retrieves information on the current status of the connection with the connector.

        :return: a ConnectorInformation message containing the current status of the connection.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.connector_monitor.getConnectorInformation(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_connector_information_stream(self, request: grpcEmpty.EmptyMessage | None = None) -> Iterator[grpcConnectionInformation.ConnectorInformation]:
        """
        Opens a stream which receives a ConnectorInformation message each second, containing the status of the
        connection with the connector.

        :return: ConnectorInformation messages containing the current status of the connection.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.connector_monitor.openConnectorInformationStream(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def get_ecu_list(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcVehicleInfo.EcuList:
        """
        Returns the ECUs that have been detected in the vehicle.

        :return: an EcuList object containing info on each detected ECU.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.vehicle_info.getEcuList(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def authenticate(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcSession.SessionToken:
        """
        Authenticates a newly created session. This needs to be done once for each session and is required to make any
        other gRPC calls for this session.

        :return: a session token, valid for 5 minutes, which is required to make gRPC calls for this session.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.session.authenticate(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def open_session_token_stream(self, request: grpcEmpty.EmptyMessage | None = None) -> Iterator[grpcSession.SessionToken]:
        """
        Starts a stream which receives a new session token every 2 minutes, each of which is valid for 5 minutes. A
        valid session token is required to make gRPC calls.

        :return: session tokens required to keep the session valid.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.session.openSessionTokenStream(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def start_context(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcFunction.FunctionContext:
        """
        Starts a new function context within the session. This creates a new context with its own isolated variables.

        :return: a session context, including a context uuid and context token, valid for 5 minutes
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        function_context = self.function.startFunctionContext(request=request, metadata=self._metadata()) # type: grpcFunction.FunctionContext

        '''Update the session information, we are now running within a context'''
        self.function_context = function_context

        '''
        Update the authentication token for this session, so we could continue with this session when it is desired.
        But in most cases we want to pass on the updated session info to another openOBD function executor, while this
        proces is monitoring (using monitor tokens) when this execution is finished.
        '''
        self.session_token = function_context.authentication_token

        '''Update the session info, so it can be passed on to another openOBD executor'''
        self.session_info.authentication_token = function_context.authentication_token

        return function_context

    @raises_openobd_exceptions
    def set_context_variable(self, key: str, value, variable_type=ContextVariableType.FUNCTION) -> None:
        if variable_type == ContextVariableType.GLOBAL:
            mem_type = grpcFunction.ContextType.GLOBAL_CONTEXT
        elif variable_type == ContextVariableType.CONNECTION:
            mem_type = grpcFunction.ContextType.CONNECTION_CONTEXT
        else:
            mem_type = grpcFunction.ContextType.FUNCTION_CONTEXT

        if isinstance(value, str):
            self.function.setVariable(
                grpcFunction.Variable(type=mem_type, key=key, value=value),
                metadata=self._metadata())
        else:
            self.function.setVariable(
                grpcFunction.Variable(type=mem_type, key=key, object=value),
                metadata=self._metadata())

    @raises_openobd_exceptions
    def get_context_variable(self, key: str, variable_type=ContextVariableType.FUNCTION) -> Variable:
        if variable_type == ContextVariableType.GLOBAL:
            mem_type = grpcFunction.ContextType.GLOBAL_CONTEXT
        elif variable_type == ContextVariableType.CONNECTION:
            mem_type = grpcFunction.ContextType.CONNECTION_CONTEXT
        else:
            mem_type = grpcFunction.ContextType.FUNCTION_CONTEXT

        return self.function.getVariable(
            grpcFunction.Variable(type=mem_type, key=key),
            metadata=self._metadata())

    @raises_openobd_exceptions
    def delete_context_variable(self, key: str, variable_type=ContextVariableType.FUNCTION) -> None:
        if variable_type == ContextVariableType.GLOBAL:
            mem_type = grpcFunction.ContextType.GLOBAL_CONTEXT
        elif variable_type == ContextVariableType.CONNECTION:
            mem_type = grpcFunction.ContextType.CONNECTION_CONTEXT
        else:
            mem_type = grpcFunction.ContextType.FUNCTION_CONTEXT

        self.function.deleteVariable(
            grpcFunction.Variable(type=mem_type, key=key),
            metadata=self._metadata())

    @raises_openobd_exceptions
    def set_function_argument(self, key: str, value):
        self.function.setFunctionArgument(
            grpcFunction.Variable(key=key, value=value),
            metadata=self._metadata())

    @raises_openobd_exceptions
    def set_function_result(self, key: str, value):
        self.function.setFunctionResult(
            grpcFunction.Variable(key=key, value=value),
            metadata=self._metadata())

    @raises_openobd_exceptions
    def monitor_function_context(self, request: grpcFunction.FunctionContext | None = None) -> Iterator[grpcFunction.FunctionContext]:
        """
        Starts a stream which receives a new monitor token every 2 minutes, each of which is valid for 5 minutes. A
        valid monitor token is required to keep monitoring the context until it finishes.

        :return: session context containing monitor tokens and eventually a new authentication token
        """
        if request is None:
            request = grpcFunction.FunctionContext()
        return self.function.monitorFunctionContext(request=request, metadata=self._metadata(token=OpenOBDSession.MONITOR_TOKEN))

    @raises_openobd_exceptions
    def register_function_details(self, function_details: grpcFunction.FunctionDetails) -> grpcEmpty.EmptyMessage:
        """
        Registers information about what function is running in the current context.

        :param function_details: a FunctionDetails message detailing what function is running in this context.
        :return: an EmptyMessage, indicating that no problems occurred.
        """
        return self.function.registerFunctionDetails(request=function_details, metadata=self._metadata())

    @raises_openobd_exceptions
    def get_function_details(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcFunction.FunctionDetails:
        """
        Retrieves the function details that have been registered in the current context.

        :return: the current context's FunctionDetails.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.function.getFunctionDetails(request=request, metadata=self._metadata())

    @raises_openobd_exceptions
    def finish(self, service_result: grpcServiceResult.ServiceResult) -> grpcEmpty.EmptyMessage:
        """
        Gracefully closes the openOBD session by changing the session's state to "finished" and preventing further
        communication with the session. The given ServiceResult indicates the success or failure reason of the executed
        service.

        :param service_result: a ServiceResult message representing the result of the executed service.
        :return: an EmptyMessage, indicating that no problems occurred.
        """
        self.active = False
        return self.session.finish(service_result, metadata=self._metadata())

    def __str__(self):
        return (f"ID: {self.session_info.id}, "
                f"state: {self.session_info.state}, "
                f"created at: {self.session_info.created_at}, "
                f"gRPC endpoint: {self.session_info.grpc_endpoint}, "
                f"authentication token: {self.session_info.authentication_token}")
