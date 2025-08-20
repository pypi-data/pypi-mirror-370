#!/usr/bin/env python3
"""
Data collection from RedZ LKM144 energy meter via Modbus RTU/TCP
Based on Node-RED implementation with 48 register reading
"""

import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import serial
from pymodbus.client.serial import ModbusSerialClient
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ModbusException, ConnectionException

# Import shared configuration classes
from ..common import CounterConfiguration, ModbusTCPConfiguration, ModbusRTUConfiguration

# Event logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModbusErrorManager:
    """Modbus error manager based on Node-RED subflow with threshold of 5"""

    def __init__(self, counter_name: str, company_id: str):
        self.counter_name = counter_name
        self.company_id = company_id
        self.error_count = 0
        self.last_error_state = False

    def process_error(self, has_error: bool) -> Optional[Dict[str, Any]]:
        """
        Process error following Node-RED logic:
        - Increment counter if there's an error
        - Reset if there's no error
        - Consider error only if count > 5 (specific to LKM144)
        """
        if has_error:
            self.error_count += 1
        else:
            self.error_count = 0

        current_error_state = self.error_count > 5

        # Report by exception - only report if state changed
        if current_error_state != self.last_error_state:
            self.last_error_state = current_error_state
            return self._create_error_message(current_error_state)

        return None

    def _create_error_message(self, is_error: bool) -> Dict[str, Any]:
        """Create error message based on Node-RED"""
        timestamp = datetime.now().isoformat()

        if is_error:
            topic = f"{self.company_id} Commm Error {self.counter_name} DOWN"
            message = f"{self.company_id} comunication with the counter {self.counter_name} is DOWN since {timestamp}"
        else:
            topic = f"{self.company_id} Commm Error {self.counter_name} Restored"
            message = f"{self.company_id} comunication with the counter {self.counter_name} has restored at {timestamp}"

        return {
            "topic": topic,
            "message": message,
            "timestamp": timestamp,
            "error_state": is_error
        }


class LKM144DataCollector:
    """RedZ LKM144 data collection"""

    def __init__(self, counter_config: CounterConfiguration,
                 modbus_tcp_config: Optional[ModbusTCPConfiguration] = None,
                 modbus_rtu_config: Optional[ModbusRTUConfiguration] = None):
        self.counter_config = counter_config
        self.modbus_tcp_config = modbus_tcp_config
        self.modbus_rtu_config = modbus_rtu_config
        self.client = None
        self.connection_type = None
        self.error_manager = ModbusErrorManager(
            counter_config.counter_name,
            counter_config.company_id
        )

        # Validate that at least one configuration was provided
        if not self.modbus_tcp_config and not self.modbus_rtu_config:
            raise ValueError("Must provide at least one Modbus configuration (TCP or RTU)")

    def connect(self) -> bool:
        """Establish Modbus RTU or TCP connection"""
        try:
            # Try RTU first (primary for LKM144), then TCP as fallback
            if self.modbus_rtu_config:
                return self._connect_rtu()
            elif self.modbus_tcp_config:
                return self._connect_tcp()
            
            return False

        except Exception as e:
            logger.error(f"Error connecting: {e}")
            return False

    def _connect_rtu(self) -> bool:
        """Establish Modbus RTU connection"""
        try:
            self.client = ModbusSerialClient(
                port=self.modbus_rtu_config.port,
                baudrate=self.modbus_rtu_config.baudrate,
                bytesize=self.modbus_rtu_config.data_bits,
                parity=self.modbus_rtu_config.parity,
                stopbits=self.modbus_rtu_config.stop_bits,
                timeout=self.modbus_rtu_config.timeout
            )

            if self.client.connect():
                self.connection_type = "RTU"
                logger.info(f"Connected to Modbus RTU device on port {self.modbus_rtu_config.port}")
                return True
            else:
                logger.error("Failed to connect to Modbus RTU device")
                # Try TCP if available
                if self.modbus_tcp_config:
                    return self._connect_tcp()
                return False

        except Exception as e:
            logger.error(f"RTU connection error: {e}")
            # Try TCP if available
            if self.modbus_tcp_config:
                return self._connect_tcp()
            return False

    def _connect_tcp(self) -> bool:
        """Establish Modbus TCP connection"""
        try:
            self.client = ModbusTcpClient(
                host=self.modbus_tcp_config.host,
                port=self.modbus_tcp_config.port,
                timeout=self.modbus_tcp_config.timeout
            )

            if self.client.connect():
                self.connection_type = "TCP"
                logger.info(f"Connected to Modbus TCP device at {self.modbus_tcp_config.host}:{self.modbus_tcp_config.port}")
                return True
            else:
                logger.error("Failed to connect to Modbus TCP device")
                return False

        except Exception as e:
            logger.error(f"TCP connection error: {e}")
            return False

    def disconnect(self):
        """Close the Modbus connection"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from Modbus {self.connection_type} device")

    def _read_registers(self, address: int, count: int) -> Optional[list]:
        """Read holding registers from the device"""
        try:
            if not self.client or not self.client.is_socket_open():
                raise ConnectionException("Client not connected")

            result = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=self.counter_config.unit_id
            )

            if result.isError():
                raise ModbusException(f"Read error: {result}")

            return result.registers

        except Exception as e:
            logger.error(f"Error reading registers {address}-{address + count - 1}: {e}")
            return None

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect all data following Node-RED LKM144 sequence"""
        timestamp = datetime.now().isoformat()

        try:
            # Read all 48 registers in one operation (address 0x00, quantity 48)
            registers = self._read_registers(0x00, 48)
            if registers is None:
                self._process_communication_error()
                return None

            # Process communication success
            error_msg = self.error_manager.process_error(False)
            if error_msg:
                logger.info(f"Communication restored: {error_msg['message']}")

            # Parse and format data according to Node-RED buffer-parser
            formatted_data = self._parse_lkm144_data(registers, timestamp)
            return formatted_data

        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            self._process_communication_error()
            return None

    def _process_communication_error(self):
        """Process communication error"""
        error_msg = self.error_manager.process_error(True)
        if error_msg:
            logger.warning(f"Communication error: {error_msg['message']}")

    def _parse_lkm144_data(self, registers: list, timestamp: str) -> Dict[str, Any]:
        """
        Parse LKM144 data according to Node-RED buffer-parser specification
        48 registers = 96 bytes, parsed as 24 uint32be values
        """
        
        def uint32_from_registers(reg_offset: int) -> int:
            """Extract uint32be value from register pair starting at offset"""
            if reg_offset + 1 >= len(registers):
                return 0
            # Big-endian: high register first, then low register
            return (registers[reg_offset] << 16) + registers[reg_offset + 1]

        return {
            "companyId": self.counter_config.company_id,
            "timestamp": timestamp,
            "counterId": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # Time and date
            "time": uint32_from_registers(0),
            "date": uint32_from_registers(2),

            # Energy values
            "energyActive": uint32_from_registers(4),
            "energyActiveExport": uint32_from_registers(6),  # Total active energy export A-
            "energyReactiveImport": uint32_from_registers(8),  # Total reactive energy R+
            "energyReactiveExport": uint32_from_registers(10),  # Total reactive energy R-
            "energyReactive": uint32_from_registers(12),
            "energyReactiveCapacitiveImport": uint32_from_registers(14),  # Rc+ Q2
            "energyReactiveInductiveExport": uint32_from_registers(16),  # Ri- Q3
            "energyReactiveCapacitiveExport": uint32_from_registers(18),  # Rc- Q4

            # Power values
            "maxPowerImport": uint32_from_registers(20),  # P+max
            "maxPowerExport": uint32_from_registers(22),  # P-max
            "avgPowerImport": uint32_from_registers(24),  # P+max last period
            "instantaneousPower": uint32_from_registers(26),  # P+ instantaneous

            # Current measurements (L1, L2, L3)
            "currentL1": uint32_from_registers(28),
            "currentL2": uint32_from_registers(30),
            "currentL3": uint32_from_registers(32),

            # Voltage measurements (L1, L2, L3)
            "voltageL1": uint32_from_registers(34),
            "voltageL2": uint32_from_registers(36),
            "voltageL3": uint32_from_registers(38),

            # Power factor and frequency
            "powerFactor": uint32_from_registers(40),
            "frequency": uint32_from_registers(42),

            # Meter identification and sum power
            "meterNumber": uint32_from_registers(44),
            "sumActivePower": uint32_from_registers(46)  # A+ - A-
        }


def main():
    """Main function for testing"""
    # Counter configuration (matching Node-RED Red Z#10)
    counter_config = CounterConfiguration(
        counter_id=200,
        unit_id=1,
        counter_name="e-Redes",
        company_id="TestCompany"
    )

    # Modbus RTU configuration (primary, matching Node-RED)
    modbus_rtu_config = ModbusRTUConfiguration(
        port="/dev/ttyNS0",
        baudrate=9600
    )

    # Optional TCP configuration (fallback)
    modbus_tcp_config = ModbusTCPConfiguration(
        host="192.162.10.10",
        port=502
    )

    # Create collector
    collector = LKM144DataCollector(
        counter_config, 
        modbus_tcp_config=modbus_tcp_config,
        modbus_rtu_config=modbus_rtu_config
    )

    try:
        # Connect
        if not collector.connect():
            logger.error("Failed to connect. Exiting...")
            return

        # Collection loop
        logger.info("Starting data collection...")
        while True:
            data = collector.collect_data()

            if data:
                # Here you can process data as needed
                # For example: save to database, send via MQTT, etc.
                print(json.dumps(data, indent=2, ensure_ascii=False))

            # Interval between readings (adjust as needed)
            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("Stopping data collection...")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        collector.disconnect()


if __name__ == "__main__":
    main()