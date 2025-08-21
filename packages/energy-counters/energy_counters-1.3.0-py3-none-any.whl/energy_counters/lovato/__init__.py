"""
Lovato Counter Modules

This module provides interfaces for Lovato energy meters and counters.

Available counters:
- DMG6: Complete implementation with TCP and RTU support (previously named DMG210)
- DMG210: Complete implementation with TCP and RTU support (based on Node-RED flow)
- DMG1: Complete implementation with TCP and RTU support (based on Node-RED flow)
- DMG800: Complete implementation with TCP and RTU support (based on Node-RED flow)
"""

from .dmg6 import (
    ModbusErrorManager as DMG6ModbusErrorManager,
    DMG6DataCollector
)
from .dmg210 import (
    ModbusErrorManager,
    DMG210DataCollector
)
from .dmg1 import (
    ModbusErrorManager as DMG1ModbusErrorManager,
    DMG1DataCollector
)
from .dmg800 import (
    ModbusErrorManager as DMG800ModbusErrorManager,
    DMG800DataCollector
)

# Import shared configuration classes
from ..common import CounterConfiguration, ModbusTCPConfiguration, ModbusRTUConfiguration

__all__ = [
    'CounterConfiguration',
    'ModbusTCPConfiguration', 
    'ModbusRTUConfiguration',
    'ModbusErrorManager',
    'DMG6ModbusErrorManager',
    'DMG6DataCollector',
    'DMG210DataCollector',
    'DMG1ModbusErrorManager',
    'DMG1DataCollector',
    'DMG800ModbusErrorManager',
    'DMG800DataCollector'
]