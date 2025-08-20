"""
Carlo Gavazzi Counter Modules

This module provides interfaces for Carlo Gavazzi energy meters and counters.

Available counters:
- EM530: Energy meter with Modbus RTU and TCP communication
"""

from .em530 import (
    CounterConfiguration,
    ModbusConfiguration,
    ModbusTCPConfiguration,
    ModbusRTUConfiguration,
    ModbusErrorManager,
    EM530DataCollector
)

__all__ = [
    'CounterConfiguration',
    'ModbusConfiguration',
    'ModbusTCPConfiguration',
    'ModbusRTUConfiguration', 
    'ModbusErrorManager',
    'EM530DataCollector'
]