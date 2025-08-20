"""
Contrel Counter Modules

This module provides interfaces for Contrel energy meters and counters.

Available counters:
- uD3h: Energy meter with Modbus TCP/RTU support
"""

from .ud3h import (
    UD3hDataCollector,
    CounterConfiguration,
    ModbusTCPConfiguration,
    ModbusRTUConfiguration,
    ModbusErrorManager
)

__all__ = [
    "UD3hDataCollector",
    "CounterConfiguration", 
    "ModbusTCPConfiguration",
    "ModbusRTUConfiguration",
    "ModbusErrorManager"
]