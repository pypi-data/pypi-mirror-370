#!/usr/bin/env python3
"""
Data collection from Carlo Gavazzi EM530 counter via Modbus RTU
"""

import time
import json
import logging
from datetime import datetime
from dataclasses import dataclass
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


@dataclass
class ModbusConfiguration:
    """Modbus connection configuration (backward compatibility)"""
    port: str = "/dev/ttyAMA0"
    baudrate: int = 9600
    data_bits: int = 8
    parity: str = 'N'
    stop_bits: int = 1
    timeout: float = 2.0


class ModbusErrorManager:
    """Modbus error manager based on Node-RED subflow"""

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
        - Consider error only if count > 2
        """
        if has_error:
            self.error_count += 1
        else:
            self.error_count = 0

        current_error_state = self.error_count > 2

        # Report by exception - only report if state changed
        if current_error_state != self.last_error_state:
            self.last_error_state = current_error_state
            return self._create_error_message(current_error_state)

        return None

    def _create_error_message(self, is_error: bool) -> Dict[str, Any]:
        """Create error message based on Node-RED"""
        timestamp = datetime.now().isoformat()

        if is_error:
            topic = f"{self.company_id} Communication Error {self.counter_name} INACTIVE"
            message = f"{self.company_id} communication with counter {self.counter_name} is INACTIVE since {timestamp}"
        else:
            topic = f"{self.company_id} Communication Error {self.counter_name} Restored"
            message = f"{self.company_id} communication with counter {self.counter_name} was restored at {timestamp}"

        return {
            "topic": topic,
            "message": message,
            "timestamp": timestamp,
            "error_state": is_error
        }


class EM530DataCollector:
    """Carlo Gavazzi EM530 data collection"""

    def __init__(self, counter_config: CounterConfiguration, 
                 modbus_config: Optional[ModbusConfiguration] = None,
                 modbus_tcp_config: Optional[ModbusTCPConfiguration] = None,
                 modbus_rtu_config: Optional[ModbusRTUConfiguration] = None):
        self.counter_config = counter_config
        self.modbus_config = modbus_config  # For backward compatibility
        self.modbus_tcp_config = modbus_tcp_config
        self.modbus_rtu_config = modbus_rtu_config
        self.client = None
        self.connection_type = None
        self.error_manager = ModbusErrorManager(
            counter_config.counter_name,
            counter_config.company_id
        )

        # Convert legacy configuration to RTU if provided
        if modbus_config and not modbus_rtu_config:
            self.modbus_rtu_config = ModbusRTUConfiguration(
                port=modbus_config.port,
                baudrate=modbus_config.baudrate,
                data_bits=modbus_config.data_bits,
                parity=modbus_config.parity,
                stop_bits=modbus_config.stop_bits,
                timeout=modbus_config.timeout
            )

        # Validate that at least one configuration was provided
        if not self.modbus_tcp_config and not self.modbus_rtu_config:
            raise ValueError("Must provide at least one Modbus configuration (TCP, RTU or legacy)")

    def connect(self) -> bool:
        """Establish Modbus TCP or RTU connection"""
        try:
            # Try TCP first, if available
            if self.modbus_tcp_config:
                return self._connect_tcp()
            elif self.modbus_rtu_config:
                return self._connect_rtu()
            
            return False

        except Exception as e:
            logger.error(f"Error connecting: {e}")
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
            # If TCP fails, try RTU if available
            if self.modbus_rtu_config:
                return self._connect_rtu()
            return False

    def _connect_rtu(self) -> bool:
        """Establish Modbus RTU connection"""
        try:
            self.client = ModbusSerialClient(
                method='rtu',
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
                return False

        except Exception as e:
            logger.error(f"RTU connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from Modbus {self.connection_type} device")

    def read_registers(self, address: int, count: int) -> Optional[list]:
        """Read Modbus registers with error handling"""
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
        """Collect all data following Node-RED sequence"""
        timestamp = datetime.now().isoformat()

        try:
            # Read 1: Address 0x0000, 64 registers (main data)
            data01 = self.read_registers(0x0000, 64)
            if data01 is None:
                self._process_communication_error()
                return None

            # Read 2: Address 0x0056, 2 registers (apparent energy)
            data02 = self.read_registers(0x0056, 2)
            if data02 is None:
                self._process_communication_error()
                return None

            # Read 3: Address 0x0082, 6 registers (current THD)
            data03 = self.read_registers(0x0082, 6)
            if data03 is None:
                self._process_communication_error()
                return None

            # Read 4: Address 0x0092, 6 registers (voltage THD)
            data04 = self.read_registers(0x0092, 6)
            if data04 is None:
                self._process_communication_error()
                return None

            # Process communication success
            error_msg = self.error_manager.process_error(False)
            if error_msg:
                logger.info(f"Communication restored: {error_msg['message']}")

            # Format data according to Node-RED function
            formatted_data = self._format_data(data01, data02, data03, data04, timestamp)
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

    def _format_data(self, data01: list, data02: list, data03: list, data04: list, timestamp: str) -> Dict[str, Any]:
        """
        Format data according to Node-RED function
        """

        def combine_registers(high_reg: int, low_reg: int) -> int:
            """Combine two 16-bit registers into a 32-bit value"""
            return (high_reg << 16) + low_reg

        return {
            "companyId": self.counter_config.company_id,
            "timestamp": timestamp,
            "counterId": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # L-N Voltages (V)
            "voltageL1": round(combine_registers(data01[1], data01[0]) * 0.1, 1),
            "voltageL2": round(combine_registers(data01[3], data01[2]) * 0.1, 1),
            "voltageL3": round(combine_registers(data01[5], data01[4]) * 0.1, 1),

            # L-L Voltages (V)
            "voltageL12": round(combine_registers(data01[7], data01[6]) * 0.1, 1),
            "voltageL23": round(combine_registers(data01[9], data01[8]) * 0.1, 1),
            "voltageL31": round(combine_registers(data01[11], data01[10]) * 0.1, 1),

            # Currents (A)
            "currentL1": round(combine_registers(data01[13], data01[12]) * 0.001, 3),
            "currentL2": round(combine_registers(data01[15], data01[14]) * 0.001, 3),
            "currentL3": round(combine_registers(data01[17], data01[16]) * 0.001, 3),

            # Phase Powers (kW)
            "powerL1": round(combine_registers(data01[19], data01[18]) * 0.0001, 4),
            "powerL2": round(combine_registers(data01[21], data01[20]) * 0.0001, 4),
            "powerL3": round(combine_registers(data01[23], data01[22]) * 0.0001, 4),

            # Total Powers
            "activePower": round(combine_registers(data01[41], data01[40]) * 0.1, 1),  # kW
            "reactivePower": round(combine_registers(data01[45], data01[44]) * 0.1, 1),  # kVAr
            "apparentPower": round(combine_registers(data01[43], data01[42]) * 0.1, 1),  # kVA
            "powerFactor": round(data01[49] * 0.001, 3),  # Power factor

            # Frequency (Hz)
            "frequency": round(data01[51] * 0.1, 1),

            # Energies (kWh/kVArh)
            "energyActive": round(combine_registers(data01[53], data01[52]) * 0.1, 1),
            "energyReactive": round(combine_registers(data01[55], data01[54]) * 0.1, 1),
            "energyApparent": round(combine_registers(data02[1], data02[0]) * 0.1, 1),

            # Current THD (%)
            "thdCurrentL1": round(combine_registers(data03[1], data03[0]) * 0.01, 2),
            "thdCurrentL2": round(combine_registers(data03[3], data03[2]) * 0.01, 2),
            "thdCurrentL3": round(combine_registers(data03[5], data03[4]) * 0.01, 2),

            # Voltage THD (%)
            "thdVoltageL1": round(combine_registers(data04[1], data04[0]) * 0.01, 2),
            "thdVoltageL2": round(combine_registers(data04[3], data04[2]) * 0.01, 2),
            "thdVoltageL3": round(combine_registers(data04[5], data04[4]) * 0.01, 2)
        }


def main():
    """Main function"""
    # Counter configuration (adjust as needed)
    counter_config = CounterConfiguration(
        counter_id=167,
        unit_id=100,  # Modbus address of the counter
        counter_name="TestCounter",
        company_id="MyCompany"
    )

    # Modbus TCP configuration (adjust as needed)
    modbus_tcp_config = ModbusTCPConfiguration(
        host="192.162.10.10",  # Adjust to your counter's IP
        port=502
    )

    # Modbus RTU configuration (as fallback)
    modbus_rtu_config = ModbusRTUConfiguration(
        port="/dev/ttyNS0",  # Adjust according to your system
        baudrate=9600
    )

    # Create collector with both configurations (TCP has priority)
    collector = EM530DataCollector(counter_config, 
                                 modbus_tcp_config=modbus_tcp_config,
                                 modbus_rtu_config=modbus_rtu_config)

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