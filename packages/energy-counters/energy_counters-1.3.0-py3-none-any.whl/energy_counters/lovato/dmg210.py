#!/usr/bin/env python3
"""
Data collection from Lovato DMG210 counter via Modbus RTU/TCP
Based on Node-Red flow provided in issue #19
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
        - Consider error only if count > 6 (based on Node-RED flow)
        """
        if has_error:
            self.error_count += 1
        else:
            self.error_count = 0

        current_error_state = self.error_count > 6

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
            message = f"{self.company_id} communication with the counter {self.counter_name} is DOWN since {timestamp}"
        else:
            topic = f"{self.company_id} Commm Error {self.counter_name} Restored"
            message = f"{self.company_id} communication with the counter {self.counter_name} has restored at {timestamp}"

        return {
            "topic": topic,
            "message": message,
            "timestamp": timestamp,
            "error_state": is_error
        }


class DMG210DataCollector:
    """Lovato DMG210 data collection"""

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
        if not modbus_tcp_config and not modbus_rtu_config:
            raise ValueError("Must provide at least one Modbus configuration (TCP or RTU)")

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
                device_id=self.counter_config.unit_id
            )

            if result.isError():
                raise ModbusException(f"Read error: {result}")

            return result.registers

        except Exception as e:
            logger.error(f"Error reading registers {address}-{address + count - 1}: {e}")
            return None

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect all data following Node-RED DMG210 sequence"""
        timestamp = datetime.now().isoformat()

        try:
            # Read 1: Address 2, 24 registers (instantaneous data)
            data01 = self.read_registers(2, 24)
            if data01 is None:
                self._process_communication_error()
                return None

            # Read 2: Address 0x32 (50), 38 registers (frequency, equivalents, THD)
            data02 = self.read_registers(0x32, 38)
            if data02 is None:
                self._process_communication_error()
                return None

            # Read 3: Address 6687, 10 registers (energies)
            data03 = self.read_registers(6687, 10)
            if data03 is None:
                self._process_communication_error()
                return None

            # Process communication success
            error_msg = self.error_manager.process_error(False)
            if error_msg:
                logger.info(f"Communication restored: {error_msg['message']}")

            # Format data according to Node-RED function
            formatted_data = self._format_data(data01, data02, data03, timestamp)
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

    def _format_data(self, data01: list, data02: list, data03: list, timestamp: str) -> Dict[str, Any]:
        """
        Format data according to Node-RED DMG210 configuration
        Based on the buffer parsers in the Node-RED flow
        """

        def uint32_from_registers(high_reg: int, low_reg: int) -> int:
            """Convert two 16-bit registers to uint32 big-endian value"""
            return (high_reg << 16) + low_reg

        def int32_from_registers(high_reg: int, low_reg: int) -> int:
            """Convert two 16-bit registers to int32 big-endian value"""
            value = (high_reg << 16) + low_reg
            # Convert to signed int32
            if value > 0x7FFFFFFF:
                value -= 0x100000000
            return value

        return {
            "companyId": self.counter_config.company_id,
            "timestamp": timestamp,
            "counterId": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # Instantaneous data (data01) - based on second buffer parser
            # L-N Voltages (V) - uint32be scale 0.01
            "voltageL1": round(uint32_from_registers(data01[0], data01[1]) * 0.01, 2),
            "voltageL2": round(uint32_from_registers(data01[2], data01[3]) * 0.01, 2),
            "voltageL3": round(uint32_from_registers(data01[4], data01[5]) * 0.01, 2),

            # Currents (A) - uint32be scale 0.0001
            "currentL1": round(uint32_from_registers(data01[6], data01[7]) * 0.0001, 4),
            "currentL2": round(uint32_from_registers(data01[8], data01[9]) * 0.0001, 4),
            "currentL3": round(uint32_from_registers(data01[10], data01[11]) * 0.0001, 4),

            # L-L Voltages (V) - uint32be scale 0.01
            "voltageL12": round(uint32_from_registers(data01[12], data01[13]) * 0.01, 2),
            "voltageL23": round(uint32_from_registers(data01[14], data01[15]) * 0.01, 2),
            "voltageL31": round(uint32_from_registers(data01[16], data01[17]) * 0.01, 2),

            # Phase Powers (kW) - int32be scale 0.01
            "powerL1": round(int32_from_registers(data01[18], data01[19]) * 0.01, 2),
            "powerL2": round(int32_from_registers(data01[20], data01[21]) * 0.01, 2),
            "powerL3": round(int32_from_registers(data01[22], data01[23]) * 0.01, 2),

            # Frequency and equivalent data (data02) - based on instant parser
            # Frequency (Hz) - uint32be scale 0.01
            "frequency": round(uint32_from_registers(data02[0], data02[1]) * 0.01, 2),

            # Equivalent values
            "veq": round(uint32_from_registers(data02[2], data02[3]) * 0.01, 2),
            "veql": round(uint32_from_registers(data02[4], data02[5]) * 0.01, 2),
            "ieq": round(uint32_from_registers(data02[6], data02[7]) * 0.0001, 4),

            # Equivalent Powers (kW/kVAr/kVA) - int32be/uint32be scale 0.01
            "activePower": round(int32_from_registers(data02[8], data02[9]) * 0.01, 2),
            "reactivePower": round(int32_from_registers(data02[10], data02[11]) * 0.01, 2),
            "apparentPower": round(uint32_from_registers(data02[12], data02[13]) * 0.01, 2),
            "powerFactor": round(uint32_from_registers(data02[14], data02[15]) * 0.0001, 4),

            # Additional fields from Node-RED parser
            "assN": round(uint32_from_registers(data02[16], data02[17]) * 0.01, 2),
            "assIn": round(uint32_from_registers(data02[18], data02[19]) * 0.01, 2),
            "iln": round(uint32_from_registers(data02[20], data02[21]) * 0.01, 2),

            # Voltage THD (%) - uint32be scale 0.01
            "thdVoltageL1": round(uint32_from_registers(data02[26], data02[27]) * 0.01, 2),
            "thdVoltageL2": round(uint32_from_registers(data02[28], data02[29]) * 0.01, 2),
            "thdVoltageL3": round(uint32_from_registers(data02[30], data02[31]) * 0.01, 2),

            # Current THD (%) - uint32be scale 0.01
            "thdCurrentL1": round(uint32_from_registers(data02[32], data02[33]) * 0.01, 2),
            "thdCurrentL2": round(uint32_from_registers(data02[34], data02[35]) * 0.01, 2),
            "thdCurrentL3": round(uint32_from_registers(data02[36], data02[37]) * 0.01, 2),

            # Energies (data03) - based on energy parser int32be scale 0.01
            "energyActive": round(int32_from_registers(data03[0], data03[1]) * 0.01, 1),
            "energyReactive": round(int32_from_registers(data03[4], data03[5]) * 0.01, 1),
            "energyApparent": round(int32_from_registers(data03[8], data03[9]) * 0.01, 1),
        }


def main():
    """Main function for testing"""
    # Counter configuration (adjust as needed)
    counter_config = CounterConfiguration(
        counter_id=117,
        unit_id=83,  # Modbus address of the counter (from Node-RED flow)
        counter_name="UPS Estatica",
        company_id="MyCompany"
    )

    # Modbus TCP configuration (adjust as needed)
    modbus_tcp_config = ModbusTCPConfiguration(
        host="172.16.5.11",
        port=502
    )

    # Modbus RTU configuration (as fallback)
    modbus_rtu_config = ModbusRTUConfiguration(
        port="/dev/ttyNS0",
        baudrate=9600
    )

    # Create collector with both configurations
    collector = DMG210DataCollector(counter_config, modbus_tcp_config, modbus_rtu_config)

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