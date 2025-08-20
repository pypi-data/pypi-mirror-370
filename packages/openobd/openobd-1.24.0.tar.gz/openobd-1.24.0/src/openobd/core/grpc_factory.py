import grpc

from openobd_protocol.Communication import CommunicationServices_pb2_grpc as grpcCommunicationService
from openobd_protocol.Configuration import ConfigurationServices_pb2_grpc as grpcConfigurationService
from openobd_protocol.ConnectionMonitor import ConnectionMonitorServices_pb2_grpc as grpcConnectionMonitorService
from openobd_protocol.Function import FunctionServices_pb2_grpc as grpcFunctionService
from openobd_protocol.Session import SessionServices_pb2_grpc as grpcService
from openobd_protocol.UserInterface import UserInterfaceServices_pb2_grpc as grpcUserInterfaceService
from openobd_protocol.SessionController import SessionControllerServices_pb2_grpc as grpcSessionControllerService
from openobd_protocol.FunctionBroker import FunctionBrokerServices_pb2_grpc as grpcFunctionBrokerServices
from openobd_protocol.VehicleInfo import VehicleInfoServices_pb2_grpc as grpcVehicleInfoServices

from .exceptions import OpenOBDException

class GrpcChannel:

    m_grpc_host = None
    m_grpc_port = 443
    m_connected = False
    m_channel = None

    def __init__(self, grpc_host, grpc_port):
        self.m_grpc_host = grpc_host
        self.m_grpc_port = grpc_port

    def connect(self):
        if not self.m_connected:
            ''' Check if local grpc-proxy is running '''
            if self.m_grpc_port == 443:
                self.m_channel = grpc.secure_channel(self.m_grpc_host, grpc.ssl_channel_credentials())
            else:
                ''' NOTE: Only use this for development purposes '''
                self.m_channel = grpc.insecure_channel('{}:{}'.format(self.m_grpc_host, self.m_grpc_port))

            ''' TODO: Exceptions and stuff '''
            self.m_connected = True

    def getChannel(self):
        if not self.m_connected:
            raise OpenOBDException("Grpc channel not connected")

        return self.m_channel

class GrpcFactory:
    def get_session(self) -> grpcService.sessionStub | grpcService.sessionServicer:
        return grpcService.sessionServicer()

    def get_function(self) -> grpcFunctionService.functionStub | grpcFunctionService.functionServicer:
        return grpcFunctionService.functionServicer()

    def get_config(self) -> grpcConfigurationService.configStub | grpcConfigurationService.configServicer:
        return grpcConfigurationService.configServicer()

    def get_can(self) -> grpcCommunicationService.canStub | grpcCommunicationService.canServicer:
        return grpcCommunicationService.canServicer()

    def get_kline(self) -> grpcCommunicationService.klineStub | grpcCommunicationService.klineServicer:
        return grpcCommunicationService.klineServicer()

    def get_terminal15(self) -> grpcCommunicationService.terminal15Stub | grpcCommunicationService.terminal15Servicer:
        return grpcCommunicationService.terminal15Servicer()

    def get_doip(self) -> grpcCommunicationService.doipStub | grpcCommunicationService.doipServicer:
        return grpcCommunicationService.doipServicer()

    def get_ui(self) -> grpcUserInterfaceService.userInterfaceStub | grpcUserInterfaceService.userInterfaceServicer:
        return grpcUserInterfaceService.userInterfaceServicer()

    def get_connection_monitor(self) -> grpcConnectionMonitorService.connectionMonitorStub | grpcConnectionMonitorService.connectionMonitorServicer:
        return grpcConnectionMonitorService.connectionMonitorServicer()

    def get_session_controller(self) -> grpcSessionControllerService.sessionControllerStub | grpcSessionControllerService.sessionControllerServicer:
        return grpcSessionControllerService.sessionControllerServicer()

    def get_function_broker(self) -> grpcFunctionBrokerServices.functionBrokerStub | grpcFunctionBrokerServices.functionBrokerServicer:
        return grpcFunctionBrokerServices.functionBrokerServicer()

    def get_vehicle_info(self) -> grpcVehicleInfoServices.vehicleInfoStub | grpcVehicleInfoServices.vehicleInfoServicer:
        return grpcVehicleInfoServices.vehicleInfoServicer()

class NetworkGrpcFactory(GrpcFactory):

    def __init__(self, grpc_host=None, grpc_port=443):
        """
        A factory that returns the methods to make grpc calls via the network.
        :param grpc_host: the hostname for the grpc server
        :param grpc_port: the default value of 443 should be used to make gRPC calls using SSL.
        """
        self.grpc_channel = GrpcChannel(grpc_host, grpc_port)
        self.grpc_channel.connect()

    def get_session(self) -> grpcService.sessionStub | grpcService.sessionServicer:
        return grpcService.sessionStub(self.grpc_channel.getChannel())

    def get_function(self) -> grpcFunctionService.functionStub | grpcFunctionService.functionServicer:
        return grpcFunctionService.functionStub(self.grpc_channel.getChannel())

    def get_config(self) -> grpcConfigurationService.configStub | grpcConfigurationService.configServicer:
        return grpcConfigurationService.configStub(self.grpc_channel.getChannel())

    def get_can(self) -> grpcCommunicationService.canStub | grpcCommunicationService.canServicer:
        return grpcCommunicationService.canStub(self.grpc_channel.getChannel())

    def get_kline(self) -> grpcCommunicationService.klineStub | grpcCommunicationService.klineServicer:
        return grpcCommunicationService.klineStub(self.grpc_channel.getChannel())

    def get_terminal15(self) -> grpcCommunicationService.terminal15Stub | grpcCommunicationService.terminal15Servicer:
        return grpcCommunicationService.terminal15Stub(self.grpc_channel.getChannel())

    def get_doip(self) -> grpcCommunicationService.doipStub | grpcCommunicationService.doipServicer:
        return grpcCommunicationService.doipStub(self.grpc_channel.getChannel())

    def get_ui(self) -> grpcUserInterfaceService.userInterfaceStub | grpcUserInterfaceService.userInterfaceServicer:
        return grpcUserInterfaceService.userInterfaceStub(self.grpc_channel.getChannel())

    def get_connection_monitor(self) -> grpcConnectionMonitorService.connectionMonitorStub | grpcConnectionMonitorService.connectionMonitorServicer:
        return grpcConnectionMonitorService.connectionMonitorStub(self.grpc_channel.getChannel())

    def get_session_controller(self) -> grpcSessionControllerService.sessionControllerStub | grpcSessionControllerService.sessionControllerServicer:
        return grpcSessionControllerService.sessionControllerStub(self.grpc_channel.getChannel())

    def get_function_broker(self) -> grpcFunctionBrokerServices.functionBrokerStub | grpcFunctionBrokerServices.functionBrokerServicer:
        return grpcFunctionBrokerServices.functionBrokerStub(self.grpc_channel.getChannel())

    def get_vehicle_info(self) -> grpcVehicleInfoServices.vehicleInfoStub | grpcVehicleInfoServices.vehicleInfoServicer:
        return grpcVehicleInfoServices.vehicleInfoStub(self.grpc_channel.getChannel())