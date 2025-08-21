"""
Schneider Counter Modules

This module provides interfaces for Schneider energy meters and counters.

Available counters:
- IEM3255: Complete implementation with TCP and RTU support (Counter ID 130)
- IEM3155: Complete implementation with TCP and RTU support (Counter ID 137)
- IEM3250: (To be implemented)
"""

from .iem3255 import (
    ModbusErrorManager as IEM3255ModbusErrorManager,
    IEM3255DataCollector
)

from .iem3155 import (
    ModbusErrorManager as IEM3155ModbusErrorManager,
    IEM3155DataCollector
)

# Import shared configuration classes
from ..common import CounterConfiguration, ModbusTCPConfiguration, ModbusRTUConfiguration

# TODO: Implement remaining counter classes and functions
# from .iem3250 import IEM3250DataCollector

__all__ = [
    'CounterConfiguration',
    'ModbusTCPConfiguration', 
    'ModbusRTUConfiguration',
    'IEM3255ModbusErrorManager',
    'IEM3255DataCollector',
    'IEM3155ModbusErrorManager',
    'IEM3155DataCollector'
]