#!/usr/bin/env python3
"""
Data collection from Schneider IEM3155 energy meter via Modbus TCP/RTU
Based on the same structure as IEM3255 since they are similar models
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
        - Consider error only if count > 6 (specific to IEM3155)
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


class IEM3155DataCollector:
    """Schneider IEM3155 data collection"""

    def __init__(self, counter_config: CounterConfiguration, 
                 connection_config, use_tcp: bool = True):
        """
        Initialize IEM3155 data collector
        
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
        
        # Set host IP for error reporting
        if hasattr(connection_config, 'host'):
            self.error_manager.set_host_ip(connection_config.host)

    def connect(self) -> bool:
        """Connect to the meter"""
        try:
            if self.use_tcp:
                self.client = ModbusTcpClient(
                    host=self.connection_config.host,
                    port=self.connection_config.port,
                    timeout=self.connection_config.timeout
                )
            else:
                self.client = ModbusSerialClient(
                    port=self.connection_config.port,
                    baudrate=self.connection_config.baudrate,
                    bytesize=self.connection_config.bytesize,
                    parity=self.connection_config.parity,
                    stopbits=self.connection_config.stopbits,
                    timeout=self.connection_config.timeout
                )

            connection = self.client.connect()
            if connection:
                logger.info(f"Connected to IEM3155 meter {self.counter_config.counter_name}")
                return True
            else:
                logger.error(f"Failed to connect to IEM3155 meter {self.counter_config.counter_name}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to IEM3155 meter: {e}")
            return False

    def disconnect(self):
        """Disconnect from the meter"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from IEM3155 meter {self.counter_config.counter_name}")

    def _read_registers(self, address: int, count: int) -> Optional[List[int]]:
        """Read modbus registers with error handling"""
        try:
            result = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=self.counter_config.unit_id
            )
            
            if result.isError():
                logger.error(f"Modbus error reading registers {address}-{address+count-1}: {result}")
                return None
                
            return result.registers

        except Exception as e:
            logger.error(f"Exception reading registers {address}-{address+count-1}: {e}")
            return None

    def _parse_float_be(self, registers: List[int], start_index: int) -> float:
        """Parse big-endian float from registers"""
        if start_index + 1 >= len(registers):
            return 0.0
            
        # Combine two 16-bit registers into one 32-bit value (big-endian)
        combined = (registers[start_index] << 16) | registers[start_index + 1]
        
        # Convert to bytes and then to float
        bytes_val = struct.pack('>I', combined)  # '>I' = big-endian unsigned int
        float_val = struct.unpack('>f', bytes_val)[0]  # '>f' = big-endian float
        
        return float_val

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect data from IEM3155 meter"""
        if not self.client:
            logger.error("Client not connected")
            return None

        try:
            # Read data blocks as per IEM3155 register map
            # Using same register map as IEM3255 since they're similar models
            current_data = self._read_registers(2998, 8)     # Current measurements
            voltage_data = self._read_registers(3018, 16)    # Voltage measurements  
            power_data = self._read_registers(3052, 12)      # Power measurements
            freq_data = self._read_registers(3108, 4)        # Frequency
            energy_data = self._read_registers(45098, 4)     # Energy

            # Check if any read failed
            if any(data is None for data in [current_data, voltage_data, power_data, freq_data, energy_data]):
                error_msg = self.error_manager.process_error(True)
                if error_msg:
                    logger.warning(f"Modbus communication error: {error_msg}")
                return None

            # Reset error count on successful read
            error_msg = self.error_manager.process_error(False)
            if error_msg:
                logger.info(f"Communication restored: {error_msg}")

            # Parse and format data
            return self._format_data(current_data, voltage_data, power_data, freq_data, energy_data)

        except Exception as e:
            logger.error(f"Error collecting data from IEM3155: {e}")
            error_msg = self.error_manager.process_error(True)
            if error_msg:
                logger.warning(f"Exception in data collection: {error_msg}")
            return None

    def _format_data(self, current_data: List[int], voltage_data: List[int], 
                     power_data: List[int], freq_data: List[int], 
                     energy_data: List[int]) -> Dict[str, Any]:
        """Format collected data according to Node-RED format"""
        
        timestamp = datetime.now().isoformat()
        
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

        # Format according to Node-RED function (same format as IEM3255)
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
        counter_id=137,
        unit_id=20,
        counter_name="L21 - Secadores Linhas 21 e 22",
        company_id="TestCompany"
    )
    
    tcp_config = ModbusTCPConfiguration(
        host="172.16.5.9",
        port=502,
        timeout=3.0
    )
    
    collector = IEM3155DataCollector(counter_config, tcp_config, use_tcp=True)
    
    try:
        logger.info("Starting IEM3155 data collection...")
        
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