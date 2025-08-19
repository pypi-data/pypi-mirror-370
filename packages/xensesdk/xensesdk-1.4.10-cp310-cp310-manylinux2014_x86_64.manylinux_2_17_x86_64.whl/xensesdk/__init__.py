import cypack; cypack.init(__name__, set([]));
from pathlib import Path
PROJ_DIR = Path(__file__).resolve().parent

import platform
SYSTEM = platform.system().lower()
MACHINE = platform.machine().lower()

from xensesdk.xenseInterface.XenseSensor import Sensor as Sensor
from xensesdk.omni.widgets import ExampleView as ExampleView
from xensesdk.zeroros import call_service

from ._version import __version__
__all__ = ["__version__"]