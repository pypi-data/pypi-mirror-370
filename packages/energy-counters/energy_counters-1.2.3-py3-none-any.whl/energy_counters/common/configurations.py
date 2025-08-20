#!/usr/bin/env python3
"""
Shared configuration classes for Energy Counters library.

This module contains the common configuration dataclasses that are used
across all counter modules to avoid code duplication.
"""

from dataclasses import dataclass


@dataclass
class CounterConfiguration:
    """Counter configuration
    
    Common configuration for all counter types containing basic
    identification and connection parameters.
    """
    counter_id: int
    unit_id: int
    counter_name: str
    company_id: str


@dataclass
class ModbusTCPConfiguration:
    """Modbus TCP connection configuration
    
    Configuration for Modbus TCP connections. Default values are set
    to commonly used settings, but can be overridden as needed.
    """
    host: str = "192.162.10.10"  # Default host - can be overridden
    port: int = 502              # Standard Modbus TCP port
    timeout: float = 4.0         # Connection timeout in seconds


@dataclass
class ModbusRTUConfiguration:
    """Modbus RTU connection configuration
    
    Configuration for Modbus RTU serial connections. Default values
    are set to commonly used settings, but can be overridden as needed.
    """
    port: str = "/dev/ttyAMA0"   # Default serial port - can be overridden
    baudrate: int = 9600         # Standard baudrate
    data_bits: int = 8           # Data bits
    parity: str = 'N'            # Parity (N=None, E=Even, O=Odd)
    stop_bits: int = 1           # Stop bits
    timeout: float = 2.0         # Read timeout in seconds