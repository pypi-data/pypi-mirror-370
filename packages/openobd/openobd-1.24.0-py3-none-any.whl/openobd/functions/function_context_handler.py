import threading
import time

from openobd_protocol.Session.Messages.ServiceResult_pb2 import ServiceResult
from openobd_protocol.SessionController.Messages.SessionController_pb2 import SessionInfo

from openobd.core.openobd import OpenOBD
from openobd.core.session import OpenOBDSession
from openobd.core.stream_handler import StreamHandler, OpenOBDStreamStoppedException, StreamState
from openobd.functions.function_exceptions import *

class FunctionContextHandler:

    def __init__(self, openobd_session: OpenOBDSession):
        """
        Starts a function context in the given session and starts a thread that monitors the context.

        :param openobd_session: the OpenOBDSession on which to start a context.
        """
        self.openobd_session = openobd_session

        '''Start session context'''
        self.openobd_session.start_context()

        '''Keep track of exactly this context that we want to monitor'''
        self.function_context = self.openobd_session.function_context

        '''
        Create stream handler for receiving session context updates
        The argument is the context that we want to monitor, after that we will just listen
        to an incoming stream for updates (until the context is finished)'''
        self.stream_handler = StreamHandler(self.openobd_session.monitor_function_context, request=self.openobd_session.function_context)

        self.refresh_session_context_thread = threading.Thread(target=self._monitor_session_context, daemon=True)
        self.refresh_session_context_thread.start()

    def run_function(self, function_id: str) -> FunctionContext:
        """
        Uses the OpenOBD singleton to run a function in this context and waits until it has finished.
        Raises an OpenOBDFunctionException if the function did not finish successfully.
        The context will always be closed once this method returns.

        :param function_id: the UUID of the function that needs to be executed.
        :return: a FunctionContext object containing info such as the result.
        """
        try:
            OpenOBD().run_function(function_id, self.get_session_info())
        except OpenOBDException as e:
            # Ensure this context is closed before raising an exception
            self._finish_context([Result.RESULT_FAILURE])
            if e.status == 4:  # deadline exceeded
                raise OpenOBDFunctionDeadlineExceededException(function_id=function_id) from e
            elif e.status == 7:  # permission denied
                raise OpenOBDFunctionPermissionDeniedException(function_id=function_id) from e
            elif e.status == 14:  # unavailable
                raise OpenOBDFunctionUnavailableException(function_id=function_id) from e
            else:
                raise e

        function_context = self.wait()
        self._validate_context_result(function_context, function_id)
        return function_context

    @staticmethod
    def _validate_context_result(function_context: FunctionContext, function_id: str = None):
        failure = False
        for result in function_context.service_result.result:
            if result != Result.RESULT_SUCCESS:
                failure = True
                break
        if failure or len(function_context.service_result.result) == 0:
            raise OpenOBDFunctionUnsuccessfulException(function_id=function_id, function_context=function_context)

    def _finish_context(self, results: list[Result]):
        if self.is_active():
            self.openobd_session.finish(ServiceResult(result=results))
            self.wait()     # Wait until the context has fully closed

    def get_session_info(self) -> SessionInfo:
        return self.openobd_session.session_info

    def _monitor_session_context(self):
        try:
            while True:
                function_context = self.stream_handler.receive()    # type: FunctionContext
                self.openobd_session.function_context = function_context
                if function_context.finished:
                    '''Context has finished'''
                    '''Allow authentication again from openOBD session'''
                    self.openobd_session.session_token = function_context.authentication_token
                    break

        except OpenOBDStreamStoppedException:
            pass
        except OpenOBDException as e:
            print(f" [!] openOBD session [{self.openobd_session.id()}] => " +
                  f"stopped monitoring context [{self.openobd_session.function_context.id}] due to an exception.")
            print(e)
        finally:
            self.stream_handler.stop_stream()

    def is_active(self) -> bool:
        return self.stream_handler.stream_state == StreamState.ACTIVE

    def wait(self) -> FunctionContext:
        """
        A blocking method that waits until this context has finished.

        :return: the final FunctionContext object received.
        """
        try:
            while self.is_active():
                time.sleep(1)
        except Exception:
            pass
        finally:
            return self.openobd_session.function_context
