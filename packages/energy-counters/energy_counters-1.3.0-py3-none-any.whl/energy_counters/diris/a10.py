#!/usr/bin/env python3
"""
Data collection from Diris A10 energy meter via Modbus TCP/RTU
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
        - Consider error only if count > 6 (specific to Diris A10)
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


class A10DataCollector:
    """Diris A10 data collection"""

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
                self.error_manager.set_host_ip(self.modbus_tcp_config.host)
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

    def _read_registers(self, address: int, count: int) -> Optional[list]:
        """Read holding registers from the device"""
        try:
            if not self.client or not self.client.is_socket_open():
                raise ConnectionException("Client not connected")

            result = self.client.read_holding_registers(
                address=address,
                count=count,
                device_id=self.counter_config.unit_id
            )

            if result.isError():
                logger.error(f"Modbus error reading registers {address}-{address+count-1}: {result}")
                return None

            return result.registers

        except Exception as e:
            logger.error(f"Error reading registers {address}-{address+count-1}: {e}")
            return None

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect all data following Node-RED Diris A10 sequence"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Read 1: Instant data (address 50514, quantity 36)
            data01 = self._read_registers(50514, 36)
            if data01 is None:
                self._process_communication_error()
                return None

            # Read 2: Energy data (address 50780, quantity 6)
            data02 = self._read_registers(50780, 6)
            if data02 is None:
                self._process_communication_error()
                return None

            # Read 3: THD data (address 51539, quantity 6)
            data03 = self._read_registers(51539, 6)
            if data03 is None:
                self._process_communication_error()
                return None

            # Process successful communication
            error_msg = self.error_manager.process_error(False)
            if error_msg:
                logger.info(f"Communication restored: {error_msg['message']}")

            # Format and return data
            return self._format_data(data01, data02, data03, timestamp)

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
        Format data according to Node-RED Diris A10 configuration
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

        # Parse data01 (Instant Parser) - 36 registers starting at 50514
        # uint32be values, so each takes 2 registers
        vl12 = uint32_from_registers(data01[0], data01[1])    # offset 0
        vl23 = uint32_from_registers(data01[2], data01[3])    # offset 4
        vl31 = uint32_from_registers(data01[4], data01[5])    # offset 8
        vl1 = uint32_from_registers(data01[6], data01[7])     # offset 12
        vl2 = uint32_from_registers(data01[8], data01[9])     # offset 16
        vl3 = uint32_from_registers(data01[10], data01[11])   # offset 20
        freq = uint32_from_registers(data01[12], data01[13])  # offset 24
        il1 = uint32_from_registers(data01[14], data01[15])   # offset 28
        il2 = uint32_from_registers(data01[16], data01[17])   # offset 32
        il3 = uint32_from_registers(data01[18], data01[19])   # offset 36
        iln = uint32_from_registers(data01[20], data01[21])   # offset 40
        paeq = int32_from_registers(data01[22], data01[23])   # offset 44
        qaeq = int32_from_registers(data01[24], data01[25])   # offset 48
        saeq = uint32_from_registers(data01[26], data01[27])  # offset 52
        pfeq = int32_from_registers(data01[28], data01[29])   # offset 56
        pl1 = int32_from_registers(data01[30], data01[31])    # offset 60
        pl2 = int32_from_registers(data01[32], data01[33])    # offset 64
        pl3 = int32_from_registers(data01[34], data01[35])    # offset 68

        # Parse data02 (Energy Parser) - 6 registers starting at 50780
        energyActive = uint32_from_registers(data02[0], data02[1])      # offset 0
        energyReactive = uint32_from_registers(data02[2], data02[3])    # offset 4
        energyApparent = uint32_from_registers(data02[4], data02[5])    # offset 8

        # Parse data03 (THD Parser) - 6 registers starting at 51539
        # uint16be values, so each takes 1 register
        thdV1 = data03[0]   # offset 0
        thdV2 = data03[1]   # offset 2
        thdV3 = data03[2]   # offset 4
        thdIL1 = data03[3]  # offset 6
        thdIL2 = data03[4]  # offset 8
        thdIL3 = data03[5]  # offset 10

        return {
            "companyId": self.counter_config.company_id,
            "timestamp": timestamp,
            "counterId": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # Line-to-line voltages (V) - uint32be scale 0.01
            "voltageL12": f"{(vl12 * 0.01):.2f}",
            "voltageL23": f"{(vl23 * 0.01):.2f}",
            "voltageL31": f"{(vl31 * 0.01):.2f}",
            
            # Line-to-neutral voltages (V) - uint32be scale 0.01
            "voltageL1": f"{(vl1 * 0.01):.2f}",
            "voltageL2": f"{(vl2 * 0.01):.2f}",
            "voltageL3": f"{(vl3 * 0.01):.2f}",

            # Currents (A) - uint32be scale 0.001
            "currentL1": f"{(il1 * 0.001):.2f}",
            "currentL2": f"{(il2 * 0.001):.2f}",
            "currentL3": f"{(il3 * 0.001):.2f}",

            # Phase powers (W) - int32be scale 0.01
            "powerL1": f"{(pl1 * 0.01):.2f}",
            "powerL2": f"{(pl2 * 0.01):.2f}",
            "powerL3": f"{(pl3 * 0.01):.2f}",

            # Frequency (Hz) - uint32be scale 0.01
            "frequency": f"{(freq * 0.01):.2f}",
            
            # Equivalent powers - int32be scale 0.01 for active/reactive, uint32be scale 0.01 for apparent
            "activePower": f"{(paeq * 0.01):.2f}",
            "reactivePower": f"{(qaeq * 0.01):.2f}",
            "apparentPower": f"{(saeq * 0.01):.2f}",
            
            # Power factor - int32be scale 0.001
            "powerFactor": f"{(pfeq * 0.001):.3f}",

            # Energies - uint32be scale 1
            "energyActive": str(energyActive),
            "energyReactive": str(energyReactive),
            "energyApparent": str(energyApparent),

            # THD values (%) - uint16be scale 0.1
            "thdVoltageL1": f"{(thdV1 * 0.1):.2f}",
            "thdVoltageL2": f"{(thdV2 * 0.1):.2f}",
            "thdVoltageL3": f"{(thdV3 * 0.1):.2f}",

            "thdCurrentL1": f"{(thdIL1 * 0.1):.2f}",
            "thdCurrentL2": f"{(thdIL2 * 0.1):.2f}",
            "thdCurrentL3": f"{(thdIL3 * 0.1):.2f}"
        }


def main():
    """Main function for testing"""
    # Example configuration
    counter_config = CounterConfiguration(
        counter_id=152,
        unit_id=97,
        counter_name="Carregador_Carro",
        company_id="MyCompany"
    )
    
    modbus_tcp_config = ModbusTCPConfiguration(
        host="172.16.5.11",
        port=502,
        timeout=4.0
    )
    
    # Create collector
    collector = A10DataCollector(
        counter_config=counter_config,
        modbus_tcp_config=modbus_tcp_config
    )
    
    try:
        if collector.connect():
            logger.info("Connected successfully")
            
            # Collect data
            data = collector.collect_data()
            if data:
                print("\nCollected Data:")
                print(json.dumps(data, indent=2))
            else:
                print("Failed to collect data")
                
        else:
            logger.error("Failed to connect")
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        collector.disconnect()


if __name__ == "__main__":
    main()