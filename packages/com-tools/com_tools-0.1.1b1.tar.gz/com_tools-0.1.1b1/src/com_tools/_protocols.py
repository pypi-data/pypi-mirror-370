from typing import Literal
from enum import Enum

class SupportedProtocols(str, Enum):
    DEMO = "demo"
    MODBUS = "modbus"
    SNAP7 = "snap7"
    IEC62056 = "iec62056"


