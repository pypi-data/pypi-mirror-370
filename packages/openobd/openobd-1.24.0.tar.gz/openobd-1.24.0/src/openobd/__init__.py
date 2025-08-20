# Copyright (c) 2024 Jifeline Networks B.V.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""openOBD Python Client implementation"""

try:
    # pylint: disable=ungrouped-imports
    from openobd.core import __version__
except ImportError:
    __version__ = "dev0"


'''Import the message definitions from openobd_protocol '''

'''Import the message definitions from openobd_protocol '''
from openobd_protocol.Communication.Messages.Isotp_pb2 import *
from openobd_protocol.Communication.Messages.Raw_pb2 import *
from openobd_protocol.Communication.Messages.Kline_pb2 import *
from openobd_protocol.Communication.Messages.Terminal15_pb2 import *
from openobd_protocol.Communication.Messages.Doip_pb2 import *
from openobd_protocol.Communication.Messages.Tp20_pb2 import *
from openobd_protocol.Configuration.Messages.BusConfiguration_pb2 import *
from openobd_protocol.Configuration.Messages.CanBus_pb2 import *
from openobd_protocol.Configuration.Messages.KlineBus_pb2 import *
from openobd_protocol.Configuration.Messages.Terminal15Bus_pb2 import *
from openobd_protocol.Configuration.Messages.DoipBus_pb2 import *
from openobd_protocol.ConnectionMonitor.Messages.ConnectorInformation_pb2 import *
from openobd_protocol.Messages.Empty_pb2 import *
from openobd_protocol.Session.Messages.ServiceResult_pb2 import *
from openobd_protocol.SessionController.Messages.SessionController_pb2 import *
from openobd_protocol.UserInterface.Messages.UserInterface_pb2 import *
from openobd_protocol.Function.Messages.Function_pb2 import *
from openobd_protocol.FunctionBroker.Messages.FunctionBroker_pb2 import *
from openobd_protocol.VehicleInfo.Messages.VehicleInfo_pb2 import *

'''Import all classes in subpackages for convenience'''
from .core import *
from .functions import *
from .communication import *
from .ui import *
