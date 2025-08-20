#!/usr/bin/env python3
"""
Data collection from Contrel uD3h energy meter via Modbus TCP/RTU
Based on Node-RED implementation
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
    """Modbus error manager based on Node-RED subflow with threshold of 6"""

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
        - Consider error only if count > 6 (specific to uD3h)
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
            message = f"{self.company_id}(ip:{getattr(self, '_host_ip', 'unknown')}) comunication with the counter {self.counter_name} is DOWN since {timestamp}"
        else:
            topic = f"{self.company_id} Commm Error {self.counter_name} Restored"
            message = f"{self.company_id} (ip:{getattr(self, '_host_ip', 'unknown')}) comunication with the counter {self.counter_name} has restored at {timestamp}"

        return {
            "topic": topic,
            "message": message,
            "timestamp": timestamp,
            "error_state": is_error
        }

    def set_host_ip(self, host_ip: str):
        """Set host IP for error messages"""
        self._host_ip = host_ip


class UD3hDataCollector:
    """Contrel uD3h data collection"""

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

        # Set host IP for error messages if TCP config is available
        if self.modbus_tcp_config:
            self.error_manager.set_host_ip(self.modbus_tcp_config.host)

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
        """Close the Modbus connection"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from Modbus {self.connection_type} device")

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect all data following Node-RED uD3h sequence"""
        if not self.client or not self.client.connected:
            logger.error("Not connected to Modbus device")
            self._process_communication_error()
            return None

        try:
            timestamp = datetime.now().isoformat()
            
            # Read 1: Instant data (address 4098, quantity 24)
            data01 = self._read_registers(4098, 24)
            if data01 is None:
                self._process_communication_error()
                return None

            # Read 2: Power data (address 4134, quantity 32)
            data02 = self._read_registers(4134, 32)
            if data02 is None:
                self._process_communication_error()
                return None

            # Read 3: Energy and frequency data (address 4166, quantity 6)
            data03 = self._read_registers(4166, 6)
            if data03 is None:
                self._process_communication_error()
                return None

            # Process successful communication
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

    def _read_registers(self, address: int, count: int) -> Optional[list]:
        """Read holding registers from the device"""
        try:
            result = self.client.read_holding_registers(
                address, count, unit=self.counter_config.unit_id
            )
            
            if result.isError():
                logger.error(f"Modbus error reading registers {address}-{address+count-1}: {result}")
                return None
            
            return result.registers

        except Exception as e:
            logger.error(f"Error reading registers {address}-{address+count-1}: {e}")
            return None

    def _process_communication_error(self):
        """Process communication error"""
        error_msg = self.error_manager.process_error(True)
        if error_msg:
            logger.warning(f"Communication error: {error_msg['message']}")

    def _format_data(self, data01: list, data02: list, data03: list, timestamp: str) -> Dict[str, Any]:
        """
        Format data according to Node-RED uD3h configuration
        """
        def uint32_from_registers(reg1: int, reg2: int) -> int:
            """Convert two 16-bit registers to uint32 big-endian value"""
            return (reg1 << 16) | reg2

        def int32_from_registers(reg1: int, reg2: int) -> int:
            """Convert two 16-bit registers to int32 big-endian value"""
            value = (reg1 << 16) | reg2
            # Convert to signed 32-bit if necessary
            if value >= 2**31:
                value -= 2**32
            return value

        # Parse data01 (Instant Parser) - addresses 4098-4121
        vl1 = uint32_from_registers(data01[0], data01[1])
        vl2 = uint32_from_registers(data01[2], data01[3])
        vl3 = uint32_from_registers(data01[4], data01[5])
        vl12 = uint32_from_registers(data01[6], data01[7])
        vl23 = uint32_from_registers(data01[8], data01[9])
        vl31 = uint32_from_registers(data01[10], data01[11])
        ieq = uint32_from_registers(data01[12], data01[13])
        il1 = uint32_from_registers(data01[14], data01[15])
        il2 = uint32_from_registers(data01[16], data01[17])
        il3 = uint32_from_registers(data01[18], data01[19])
        pfeq = int32_from_registers(data01[20], data01[21])

        # Parse data02 (Instant Parser 2) - addresses 4134-4165
        seq = uint32_from_registers(data02[0], data02[1])
        seq1 = uint32_from_registers(data02[2], data02[3])
        seq2 = uint32_from_registers(data02[4], data02[5])
        seq3 = uint32_from_registers(data02[6], data02[7])
        peq = uint32_from_registers(data02[8], data02[9])
        p1 = uint32_from_registers(data02[10], data02[11])
        p2 = uint32_from_registers(data02[12], data02[13])
        p3 = uint32_from_registers(data02[14], data02[15])
        qeq = uint32_from_registers(data02[16], data02[17])
        enP = uint32_from_registers(data02[24], data02[25])  # offset 48/2 = 24
        enQ = uint32_from_registers(data02[26], data02[27])  # offset 52/2 = 26

        # Parse data03 (Energy Parser) - addresses 4166-4171
        f = uint32_from_registers(data03[0], data03[1])
        enS = uint32_from_registers(data03[4], data03[5])  # offset 8/2 = 4

        return {
            "companyId": self.counter_config.company_id,
            "timestamp": timestamp,
            "counterId": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # L-L Voltages (V) - scale 1
            "voltageL12": f"{vl12:.2f}",
            "voltageL23": f"{vl23:.2f}",
            "voltageL31": f"{vl31:.2f}",
            
            # L-N Voltages (V) - scale 1
            "voltageL1": f"{vl1:.2f}",
            "voltageL2": f"{vl2:.2f}",
            "voltageL3": f"{vl3:.2f}",

            # Currents (A) - scale 0.001
            "currentL1": f"{(il1 * 0.001):.2f}",
            "currentL2": f"{(il2 * 0.001):.2f}",
            "currentL3": f"{(il3 * 0.001):.2f}",

            # Powers per phase (W) - scale 1
            "powerL1": f"{p1:.2f}",
            "powerL2": f"{p2:.2f}",
            "powerL3": f"{p3:.2f}",

            # Total powers - scale 1
            "activePower": f"{peq:.2f}",
            "reactivePower": f"{qeq:.2f}",
            "apparentPower": f"{seq:.2f}",
            "powerFactor": f"{(pfeq * 0.001):.2f}",
            
            # Frequency (Hz) - scale 0.001
            "frequency": f"{(f * 0.001):.2f}",

            # Energies - scale 0.1
            "energyActive": f"{(enP * 0.1):.1f}",
            "energyReactive": f"{(enQ * 0.1):.1f}",
            "energyApparent": f"{(enS * 0.1):.1f}",

            # THD values (hardcoded to '0' as per Node-RED)
            "thdVoltageL1": "0",
            "thdVoltageL2": "0", 
            "thdVoltageL3": "0",
            "thdCurrentL1": "0",
            "thdCurrentL2": "0",
            "thdCurrentL3": "0"
        }


def main():
    """Main function for testing"""
    # Example configuration for testing
    counter_config = CounterConfiguration(
        counter_id=125,
        unit_id=87,
        counter_name="Queimador Fieiras",
        company_id="TEST_COMPANY"
    )
    
    modbus_tcp_config = ModbusTCPConfiguration(
        host="172.16.5.11",
        port=502,
        timeout=4.0
    )
    
    collector = UD3hDataCollector(
        counter_config=counter_config,
        modbus_tcp_config=modbus_tcp_config
    )
    
    try:
        if collector.connect():
            logger.info("Connected successfully")
            
            # Collect data
            data = collector.collect_data()
            if data:
                logger.info("Data collected successfully")
                print(json.dumps(data, indent=2))
            else:
                logger.error("Failed to collect data")
        else:
            logger.error("Failed to connect")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        collector.disconnect()


if __name__ == "__main__":
    main()