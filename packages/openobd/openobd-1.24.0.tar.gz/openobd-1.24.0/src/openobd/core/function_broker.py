from typing import Iterator

from openobd_protocol.Function.Messages import Function_pb2 as grpcFunction
from openobd_protocol.FunctionBroker.Messages import FunctionBroker_pb2 as grpcFunctionBroker
from openobd_protocol.Messages import Empty_pb2 as grpcEmpty
from openobd_protocol.SessionController.Messages import SessionController_pb2 as grpcSessionController

from openobd.core._token import Token
from openobd.core.utils import _get_value_from_kwargs_or_env
from openobd.core.grpc_factory import NetworkGrpcFactory
from openobd.core.exceptions import raises_openobd_exceptions

class OpenOBDFunctionBroker:

    def __init__(self, **kwargs):
        """
        Used for hosting and running third-party openOBD functions.
        Retrieves the Partner API credentials from the environment variables unless explicitly given as kwargs.

        :keyword client_id: the identifier of the created credential set.
        :keyword client_secret: the secret of the created credential set.
        :keyword cluster_id: the ID of the cluster on which openOBD functions should be managed (001=Europe, 002=USA).
        :keyword grpc_host: the address to which gRPC calls should be sent.
        :keyword grpc_port: the port used by gRPC calls, which needs to be 443 to use SSL.
        """
        self.client_id = _get_value_from_kwargs_or_env(kwargs, "client_id", "OPENOBD_PARTNER_CLIENT_ID")
        self.client_secret = _get_value_from_kwargs_or_env(kwargs, "client_secret", "OPENOBD_PARTNER_CLIENT_SECRET")
        self.cluster_id = _get_value_from_kwargs_or_env(kwargs, "cluster_id", "OPENOBD_CLUSTER_ID")

        grpc_host = _get_value_from_kwargs_or_env(kwargs, "grpc_host", "OPENOBD_GRPC_HOST")
        grpc_port = kwargs.get('grpc_port') if 'grpc_port' in kwargs else 443

        grpc_factory = NetworkGrpcFactory(grpc_host, grpc_port)

        self.function_broker = grpc_factory.get_function_broker()
        self.function_broker_token = Token(self._request_function_broker_token, 300)

    def _metadata(self):
        metadata = [("authorization", "Bearer {}".format(self.function_broker_token.get_value()))]
        metadata = tuple(metadata)
        return metadata

    @raises_openobd_exceptions
    def _request_function_broker_token(self):
        """
        Requests a new function broker token. A valid function broker token is required to make any of the other calls
        to the function broker.
        """
        return self.function_broker.getFunctionBrokerToken(
            grpcSessionController.Authenticate(
                client_id=self.client_id,
                client_secret=self.client_secret,
                cluster_id=self.cluster_id
            )
        ).value

    @raises_openobd_exceptions
    def open_function_stream(self, function_update_messages: Iterator[grpcFunctionBroker.FunctionUpdate]) -> Iterator[grpcFunctionBroker.FunctionUpdate]:
        """
        Opens a stream in which functions can be made available for function callers, and through which function calls
        will be forwarded.

        :param function_update_messages: a FunctionUpdate message for each function that needs to be registered.
        :return: FunctionUpdate messages containing acknowledgements of registrations, pings, and function calls.
        """
        return self.function_broker.openFunctionStream(function_update_messages, metadata=self._metadata())

    @raises_openobd_exceptions
    def run_function(self, function_call: grpcFunctionBroker.FunctionCall) -> grpcFunctionBroker.FunctionUpdate:
        """
        Execute a function that has been registered by a function launcher.

        :param function_call: a FunctionCall defining which function to call, and the session to run the function in.
        :return: a FunctionUpdate object defining whether the function has been successfully launched.
        """
        return self.function_broker.runFunction(request=function_call, metadata=self._metadata())

    @raises_openobd_exceptions
    def get_function_registration(self, function_id: grpcFunction.FunctionId) -> grpcFunctionBroker.FunctionRegistration:
        """
        Retrieves information about the requested function. For instance, whether the function is online or not.

        :param function_id: the UUID of the function to request info on.
        :return: a FunctionRegistration object containing details on the requested function.
        """
        return self.function_broker.getFunctionRegistration(request=function_id, metadata=self._metadata())

    @raises_openobd_exceptions
    def generate_function_signature(self, request: grpcEmpty.EmptyMessage | None = None) -> grpcFunctionBroker.FunctionSignature:
        """
        Generates a new function ID and signature, which are used when registering an openOBD function.

        :return: a FunctionId object containing a new function ID and its corresponding signature.
        """
        if request is None:
            request = grpcEmpty.EmptyMessage()
        return self.function_broker.generateFunctionSignature(request=request, metadata=self._metadata())
