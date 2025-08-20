"""
Lovato Counter Modules

This module provides interfaces for Lovato energy meters and counters.

Available counters:
- DMG6: Complete implementation with TCP and RTU support (previously named DMG210)
- DMG210: Complete implementation with TCP and RTU support (based on Node-RED flow)
- DMG800: (To be implemented)
"""

from .dmg6 import (
    ModbusErrorManager as DMG6ModbusErrorManager,
    DMG6DataCollector
)
from .dmg210 import (
    ModbusErrorManager,
    DMG210DataCollector
)

# Import shared configuration classes
from ..common import CounterConfiguration, ModbusTCPConfiguration, ModbusRTUConfiguration

# TODO: Implement remaining counter classes and functions
# from .dmg800 import DMG800DataCollector

__all__ = [
    'CounterConfiguration',
    'ModbusTCPConfiguration', 
    'ModbusRTUConfiguration',
    'ModbusErrorManager',
    'DMG6ModbusErrorManager',
    'DMG6DataCollector',
    'DMG210DataCollector'
]