#!/usr/bin/env python3
"""
Data collection from Lovato DMG800 counter via Modbus RTU/TCP
Based on Node-RED flow pattern and existing Lovato implementations
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


class DMG800DataCollector:
    """Lovato DMG800 data collection"""

    def __init__(self, counter_config: CounterConfiguration, 
                 connection_config, use_tcp: bool = False):
        """
        Initialize DMG800 data collector
        
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
        
        # Set host IP for error reporting if using TCP
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
                    bytesize=self.connection_config.data_bits,
                    parity=self.connection_config.parity,
                    stopbits=self.connection_config.stop_bits,
                    timeout=self.connection_config.timeout
                )

            connection = self.client.connect()
            if connection:
                logger.info(f"Connected to DMG800 meter {self.counter_config.counter_name}")
                return True
            else:
                logger.error(f"Failed to connect to DMG800 meter {self.counter_config.counter_name}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to DMG800 meter: {e}")
            return False

    def disconnect(self):
        """Disconnect from the meter"""
        if self.client:
            self.client.close()
            logger.info(f"Disconnected from DMG800 meter {self.counter_config.counter_name}")

    def _read_registers(self, address: int, count: int) -> Optional[list]:
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

    def collect_data(self) -> Optional[Dict[str, Any]]:
        """Collect data from DMG800 meter following Node-RED flow pattern"""
        if not self.client:
            logger.error("Client not connected")
            return None

        timestamp = datetime.now().isoformat()

        try:
            # DMG800 follows similar pattern as DMG1 but may have different register structure
            # Based on the provided Node-RED flow fragment, using similar register map
            
            # Read 1: Address 2, 24 registers (instantaneous data)
            data01 = self._read_registers(2, 24)
            if data01 is None:
                self._process_communication_error()
                return None

            # Read 2: Address 0x32 (50), 38 registers (frequency, equivalents, THD)
            data02 = self._read_registers(0x32, 38)
            if data02 is None:
                self._process_communication_error()
                return None

            # Read 3: Address 6687, 10 registers (energies)
            data03 = self._read_registers(6687, 10)
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
            logger.error(f"Error collecting data from DMG800: {e}")
            self._process_communication_error()
            return None

    def _process_communication_error(self):
        """Process communication error"""
        error_msg = self.error_manager.process_error(True)
        if error_msg:
            logger.warning(f"Communication error: {error_msg['message']}")

    def _format_data(self, data01: list, data02: list, data03: list, timestamp: str) -> Dict[str, Any]:
        """
        Format data according to Node-RED DMG800 configuration
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
            "companyID": self.counter_config.company_id,
            "ts": timestamp,
            "counterID": str(self.counter_config.counter_id),
            "counterName": self.counter_config.counter_name,

            # Instantaneous data (data01) - similar to DMG1 structure
            # L-N Voltages (V) - uint32be scale 0.01
            "vl1": f"{uint32_from_registers(data01[0], data01[1]) * 0.01:.2f}",
            "vl2": f"{uint32_from_registers(data01[2], data01[3]) * 0.01:.2f}",
            "vl3": f"{uint32_from_registers(data01[4], data01[5]) * 0.01:.2f}",

            # Currents (A) - uint32be scale 0.0001
            "il1": f"{uint32_from_registers(data01[6], data01[7]) * 0.0001:.2f}",
            "il2": f"{uint32_from_registers(data01[8], data01[9]) * 0.0001:.2f}",
            "il3": f"{uint32_from_registers(data01[10], data01[11]) * 0.0001:.2f}",

            # L-L Voltages (V) - uint32be scale 0.01
            "vl12": f"{uint32_from_registers(data01[12], data01[13]) * 0.01:.2f}",
            "vl23": f"{uint32_from_registers(data01[14], data01[15]) * 0.01:.2f}",
            "vl31": f"{uint32_from_registers(data01[16], data01[17]) * 0.01:.2f}",

            # Phase Powers (kW) - int32be scale 0.01
            "pl1": f"{int32_from_registers(data01[18], data01[19]) * 0.01:.2f}",
            "pl2": f"{int32_from_registers(data01[20], data01[21]) * 0.01:.2f}",
            "pl3": f"{int32_from_registers(data01[22], data01[23]) * 0.01:.2f}",

            # Frequency and equivalent data (data02)
            # Frequency (Hz) - uint32be scale 0.01
            "freq": f"{uint32_from_registers(data02[0], data02[1]) * 0.01:.2f}",

            # Equivalent values from Node-RED flow
            "veq": f"{uint32_from_registers(data02[2], data02[3]) * 0.01:.2f}",
            "veql": f"{uint32_from_registers(data02[4], data02[5]) * 0.01:.2f}",
            "ieq": f"{uint32_from_registers(data02[6], data02[7]) * 0.0001:.2f}",

            # Equivalent Powers (kW/kVAr/kVA) - int32be/uint32be scale 0.01
            "paeq": f"{int32_from_registers(data02[8], data02[9]) * 0.01:.2f}",
            "qaeq": f"{int32_from_registers(data02[10], data02[11]) * 0.01:.2f}",
            "saeq": f"{uint32_from_registers(data02[12], data02[13]) * 0.01:.2f}",
            "pfeq": f"{uint32_from_registers(data02[14], data02[15]) * 0.0001:.2f}",

            # Additional fields from Node-RED parser
            "assN": f"{uint32_from_registers(data02[16], data02[17]) * 0.01:.2f}",
            "assIn": f"{uint32_from_registers(data02[18], data02[19]) * 0.01:.2f}",
            "iln": f"{uint32_from_registers(data02[20], data02[21]) * 0.01:.2f}",

            # Voltage THD (%) - uint32be scale 0.01 (if available in DMG800)
            "thdV1": f"{uint32_from_registers(data02[26], data02[27]) * 0.01:.2f}" if len(data02) > 27 else "0.00",
            "thdV2": f"{uint32_from_registers(data02[28], data02[29]) * 0.01:.2f}" if len(data02) > 29 else "0.00",
            "thdV3": f"{uint32_from_registers(data02[30], data02[31]) * 0.01:.2f}" if len(data02) > 31 else "0.00",

            # Current THD (%) - uint32be scale 0.01 (if available in DMG800)
            "thdIL1": f"{uint32_from_registers(data02[32], data02[33]) * 0.01:.2f}" if len(data02) > 33 else "0.00",
            "thdIL2": f"{uint32_from_registers(data02[34], data02[35]) * 0.01:.2f}" if len(data02) > 35 else "0.00",
            "thdIL3": f"{uint32_from_registers(data02[36], data02[37]) * 0.01:.2f}" if len(data02) > 37 else "0.00",

            # Energies (data03) - int32be scale 0.01
            "energyActive": f"{int32_from_registers(data03[0], data03[1]) * 0.01:.1f}",
            "energyReactive": f"{int32_from_registers(data03[4], data03[5]) * 0.01:.1f}",
            "energyApparent": f"{int32_from_registers(data03[8], data03[9]) * 0.01:.1f}",
        }


def main():
    """Main function for testing"""
    # Example configuration for testing DMG800
    counter_config = CounterConfiguration(
        counter_id=800,  # Example ID for DMG800
        unit_id=1,       # Default unit ID, adjust as needed
        counter_name="DMG800 Test Counter",
        company_id="TestCompany"
    )
    
    # DMG800 can use both RTU and TCP
    rtu_config = ModbusRTUConfiguration(
        port="/dev/ttyUSB0",
        baudrate=9600,
        data_bits=8,
        parity='N',
        stop_bits=1,
        timeout=3.0
    )
    
    # Alternative TCP configuration
    tcp_config = ModbusTCPConfiguration(
        host="172.16.5.12",  # Example IP
        port=502,
        timeout=4.0
    )
    
    # For this example, use RTU (change use_tcp=True for TCP)
    collector = DMG800DataCollector(counter_config, rtu_config, use_tcp=False)
    
    try:
        logger.info("Starting DMG800 data collection...")
        
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