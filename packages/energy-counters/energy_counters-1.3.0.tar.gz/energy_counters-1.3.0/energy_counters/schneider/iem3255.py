#!/usr/bin/env python3
"""
Data collection from Schneider IEM3255 energy meter via Modbus TCP/RTU
Based on Node-RED flow provided in issue #21
"""

import time
import json
import logging
import struct
from datetime import datetime
from typing import Optional, Dict, Any, List
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
        - Consider error only if count > 6 (specific to IEM3255)
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


class IEM3255DataCollector:
    """Schneider IEM3255 data collection"""

    def __init__(self, counter_config: CounterConfiguration, 
                 connection_config, use_tcp: bool = True):
        """
        Initialize IEM3255 data collector
        
        Args:
            counter_config: Counter configuration
            connection_config: TCP or RTU configuration
            use_tcp: True for TCP, False for RTU
        """
        self.counter_config = counter_config
        self.connection_config = connection_config
        self.use_tcp = use_tcp
        self.client = None
        self.error_manager = ModbusErrorManager(
            counter_config.counter_name, 
            counter_config.company_id
        )
        
        if use_tcp:
            self.error_manager.set_host_ip(connection_config.host)

    def connect(self) -> bool:
        """Establish connection with IEM3255 meter"""
        try:
            if self.use_tcp:
                self.client = ModbusTcpClient(
                    host=self.connection_config.host,
                    port=self.connection_config.port,
                    timeout=self.connection_config.timeout
                )
            else:
                self.client = ModbusSerialClient(
                    method='rtu',
                    port=self.connection_config.port,
                    baudrate=self.connection_config.baudrate,
                    timeout=self.connection_config.timeout,
                    parity=self.connection_config.parity,
                    stopbits=self.connection_config.stop_bits,
                    bytesize=self.connection_config.data_bits
                )
            
            connection_result = self.client.connect()
            if connection_result:
                logger.info(f"Connected to IEM3255 {self.counter_config.counter_name}")
                return True
            else:
                logger.error(f"Failed to connect to IEM3255 {self.counter_config.counter_name}")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from IEM3255 {self.counter_config.counter_name}")

    def _read_registers(self, address: int, count: int) -> Optional[List[int]]:
        """Read holding registers from meter"""
        try:
            if not self.client or not self.client.is_socket_open():
                if not self.connect():
                    return None
            
            result = self.client.read_holding_registers(
                address=address,
                count=count,
                unit=self.counter_config.unit_id
            )
            
            if result.isError():
                logger.error(f"Modbus error reading address {address}: {result}")
                return None
            
            return result.registers
            
        except Exception as e:
            logger.error(f"Error reading registers at address {address}: {e}")
            return None

    def _parse_float_be(self, registers: List[int], offset: int) -> float:
        """Parse big-endian float from two consecutive registers"""
        if len(registers) < offset + 2:
            return 0.0
        
        # Combine two 16-bit registers into 32-bit value (big-endian)
        raw_value = (registers[offset] << 16) | registers[offset + 1]
        
        # Convert to float using struct
        try:
            return struct.unpack('>f', raw_value.to_bytes(4, 'big'))[0]
        except Exception as e:
            logger.warning(f"Error parsing float at offset {offset}: {e}")
            return 0.0

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """
        Collect data from IEM3255 meter following Node-RED flow logic
        """
        timestamp = datetime.now().isoformat()
        has_error = False
        
        try:
            # Read current data (address 2998, 8 registers)
            current_data = self._read_registers(2998, 8)
            if current_data is None:
                has_error = True
                current_data = [0] * 8
            
            # Read voltage data (address 3018, 16 registers)  
            voltage_data = self._read_registers(3018, 16)
            if voltage_data is None:
                has_error = True
                voltage_data = [0] * 16
                
            # Read power data (address 3052, 12 registers)
            power_data = self._read_registers(3052, 12)
            if power_data is None:
                has_error = True
                power_data = [0] * 12
                
            # Read frequency data (address 3108, 4 registers)
            freq_data = self._read_registers(3108, 4)
            if freq_data is None:
                has_error = True
                freq_data = [0] * 4
                
            # Read energy data (address 45098, 4 registers)
            energy_data = self._read_registers(45098, 4)
            if energy_data is None:
                has_error = True
                energy_data = [0] * 4

            # Process error through error manager
            error_message = self.error_manager.process_error(has_error)
            if error_message:
                logger.warning(f"Error state changed: {error_message}")

            # Parse data according to Node-RED buffer parsers
            data = self._format_data(current_data, voltage_data, power_data, freq_data, energy_data, timestamp)
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting data from IEM3255: {e}")
            self.error_manager.process_error(True)
            return None

    def _format_data(self, current_data: List[int], voltage_data: List[int], 
                     power_data: List[int], freq_data: List[int], 
                     energy_data: List[int], timestamp: str) -> Dict[str, Any]:
        """
        Format data according to Node-RED IEM3255 Data Format function
        """
        
        # Parse currents from current_data (floatbe at offsets 2, 6, 10)
        il1 = self._parse_float_be(current_data, 1)  # offset 2 in bytes = index 1 in registers
        il2 = self._parse_float_be(current_data, 3)  # offset 6 in bytes = index 3 in registers  
        il3 = self._parse_float_be(current_data, 5)  # offset 10 in bytes = index 5 in registers
        
        # Parse voltages from voltage_data (floatbe at offsets 2, 6, 10, 18, 22, 26)
        vl12 = self._parse_float_be(voltage_data, 1)   # offset 2 in bytes = index 1
        vl23 = self._parse_float_be(voltage_data, 3)   # offset 6 in bytes = index 3
        vl31 = self._parse_float_be(voltage_data, 5)   # offset 10 in bytes = index 5
        vl1 = self._parse_float_be(voltage_data, 9)    # offset 18 in bytes = index 9
        vl2 = self._parse_float_be(voltage_data, 11)   # offset 22 in bytes = index 11
        vl3 = self._parse_float_be(voltage_data, 13)   # offset 26 in bytes = index 13
        
        # Parse powers from power_data (floatbe at offsets 2, 6, 10, 14)
        p1 = self._parse_float_be(power_data, 1)    # offset 2 in bytes = index 1
        p2 = self._parse_float_be(power_data, 3)    # offset 6 in bytes = index 3
        p3 = self._parse_float_be(power_data, 5)    # offset 10 in bytes = index 5
        peq = self._parse_float_be(power_data, 7)   # offset 14 in bytes = index 7
        
        # Parse frequency from freq_data (floatbe at offset 2)
        freq = self._parse_float_be(freq_data, 1)   # offset 2 in bytes = index 1
        
        # Parse energy from energy_data (floatbe at offset 2)
        energy_active = self._parse_float_be(energy_data, 1)  # offset 2 in bytes = index 1

        # Format according to Node-RED function
        formatted_data = {
            "companyID": self.counter_config.company_id,
            "ts": timestamp,
            "counterID": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,
            
            # Line-to-line voltages (from Modbus)
            "vl12": f"{vl12:.2f}",
            "vl23": f"{vl23:.2f}",
            "vl31": f"{vl31:.2f}",
            
            # Line-to-neutral voltages (hardcoded per Node-RED)
            "vl1": "0.0",
            "vl2": "0.0", 
            "vl3": "0.0",
            
            # Line currents (from Modbus)
            "il1": f"{il1:.2f}",
            "il2": f"{il2:.2f}",
            "il3": f"{il3:.2f}",
            
            # Line powers (hardcoded per Node-RED)
            "pl1": "0.0",
            "pl2": "0.0",
            "pl3": "0.0",
            
            # Equivalent powers (hardcoded per Node-RED)
            "paeq": "0.0",
            "qaeq": "0.0", 
            "saeq": "0.0",
            "pfeq": "0.0",
            
            # Frequency (from Modbus)
            "freq": f"{freq:.2f}",
            
            # Energy values
            "energyActive": f"{energy_active:.1f}",
            "energyReactive": "0.0",
            "energyApparent": "0.0",
            
            # THD values (hardcoded per Node-RED)
            "thdV1": "0.0",
            "thdV2": "0.0", 
            "thdV3": "0.0",
            "thdIL1": "0.0",
            "thdIL2": "0.0",
            "thdIL3": "0.0"
        }
        
        return formatted_data


def main():
    """Main function for testing"""
    # Example configuration for testing
    counter_config = CounterConfiguration(
        counter_id=130,
        unit_id=12,
        counter_name="L21 - Bobinadora",
        company_id="TestCompany"
    )
    
    tcp_config = ModbusTCPConfiguration(
        host="172.16.5.9",
        port=502,
        timeout=3.0
    )
    
    collector = IEM3255DataCollector(counter_config, tcp_config, use_tcp=True)
    
    try:
        logger.info("Starting IEM3255 data collection...")
        
        if not collector.connect():
            logger.error("Failed to connect to meter")
            return
            
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