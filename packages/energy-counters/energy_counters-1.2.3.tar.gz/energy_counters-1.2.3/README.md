# Energy Counters Library

[![PyPI](https://img.shields.io/pypi/v/energy-counters.svg)](https://pypi.org/project/energy-counters/)
[![Python](https://img.shields.io/pypi/pyversions/energy-counters.svg)](https://pypi.org/project/energy-counters/)
[![Wheel](https://img.shields.io/pypi/wheel/energy-counters.svg)](https://pypi.org/project/energy-counters/)
[![Status](https://img.shields.io/pypi/status/energy-counters.svg)](https://pypi.org/project/energy-counters/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintained](https://img.shields.io/badge/maintained-yes%2C%202025-success.svg)](https://github.com/nobrega8/energy-counters)

[![Downloads](https://static.pepy.tech/badge/energy-counters)](https://pepy.tech/project/energy-counters)

![Carlo Gavazzi](https://img.shields.io/badge/support-Carlo%20Gavazzi-lightgrey.svg)
![Lovato](https://img.shields.io/badge/support-Lovato-lightgrey.svg)
![Diris](https://img.shields.io/badge/support-Diris-lightgrey.svg)
![RedZ](https://img.shields.io/badge/support-RedZ-lightgrey.svg)
![Contrel](https://img.shields.io/badge/support-Contrel-lightgrey.svg)
![Schneider](https://img.shields.io/badge/support-Schneider-lightgrey.svg)

A Python library for reading data from various electrical energy counters including Carlo Gavazzi, Contrel, Diris, Lovato, RedZ, and Schneider devices.

## Features

- **Multiple Communication Protocols**: Support for both Modbus RTU (serial) and Modbus TCP connections
- **Automatic Fallback**: Intelligent switching between TCP and RTU when both are configured
- **Comprehensive Data Collection**: Read voltage, current, power, energy, and frequency measurements
- **Easy Configuration**: Simple dataclass-based configuration for counters and connections
- **Detailed Logging**: Built-in logging for debugging and monitoring
- **Modern Python**: Written for Python 3.8+ with type hints and dataclasses
- **Extensible Design**: Easy to add support for new counter models

## Installation

Install from [PyPI](https://pypi.org/project/energy-counters/):

```bash
pip install energy-counters
```

Or for development:
```bash
pip install -e .
```

## Quick Start

### Import the library

```python
import energy_counters
from energy_counters.carlo_gavazzi import EM530DataCollector
from energy_counters.lovato import DMG210DataCollector
# ... other counters
```

### Basic Usage Example

```python
from energy_counters.carlo_gavazzi import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    EM530DataCollector
)

# Configure the counter
counter_config = CounterConfiguration(
    counter_id=167,
    unit_id=100,
    counter_name="TestCounter",
    company_id="MyCompany"
)

# Configure Modbus TCP connection
tcp_config = ModbusTCPConfiguration(
    host="192.162.10.10",
    port=502
)

# Create collector and read data
collector = EM530DataCollector(counter_config, modbus_tcp_config=tcp_config)
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['voltageL1']}V")
        print(f"Current L1: {data['currentL1']}A")
        print(f"Active Power: {data['activePower']}kW")
    collector.disconnect()
```

For detailed usage examples and complete documentation for each counter, see the README files in their respective folders:
- [Carlo Gavazzi Counters](src/energy_counters/carlo_gavazzi/README.md)
- [Lovato Counters](src/energy_counters/lovato/README.md)
- [Diris Counters](src/energy_counters/diris/README.md)
- [RedZ Counters](src/energy_counters/redz/README.md)
- [Contrel Counters](src/energy_counters/contrel/README.md)
- [Schneider Counters](src/energy_counters/schneider/README.md)

## Supported Counters

| Brand | Model | Status | Modbus RTU | Modbus TCP | Features |
|-------|-------|--------|------------|------------|----------|
| **Carlo Gavazzi** | EM530 | **Implemented** | Yes | Yes | Full energy monitoring, fallback support |
| **Lovato** | DMG210 | **Implemented** | Yes | Yes | Complete energy data collection, dual communication |
| **Lovato** | DMG800 | **Planned** | - | - | Module structure ready |
| **Lovato** | DMG6 | **Implemented** | Yes | Yes | Complete energy data collection, dual communication |
| **Contrel** | uD3h | **Implemented** | Yes | Yes | Complete energy monitoring, dual communication |
| **Diris** | A10 | **Implemented** | Yes | Yes | Complete energy monitoring, THD analysis, dual communication |
| **RedZ** | LKM144 | **Implemented** | Yes | Yes | Complete energy monitoring, dual communication |
| **Schneider** | IEM3250 | **Planned** | - | - | Module structure ready |
| **Schneider** | IEM3155 | **Planned** | - | - | Module structure ready |

### Implementation Status Legend
- **Implemented**: Full functionality with comprehensive data collection
- **Planned**: Module structure exists, implementation pending
- **Modbus RTU/TCP**: Protocol supported
- **Fallback Support**: Automatic failover between TCP and RTU connections

## Requirements

- Python 3.8+
- pymodbus 3.0.0+
- pyserial 3.5+

## License

MIT License

## Contributing

We welcome contributions to the Energy Counters Library! Whether you're fixing bugs, adding new counter support, improving documentation, or suggesting features, your help is appreciated.

### Quick Start for Contributors

1. **Fork the repository** and clone your fork
2. **Set up the development environment** (see [CONTRIBUTING.md](CONTRIBUTING.md))
3. **Create a feature branch** for your changes
4. **Make your changes** following our coding standards
5. **Test thoroughly** with actual hardware when possible
6. **Submit a pull request** with a clear description

### What We Need Help With

- **New Counter Support:** Implementing support for additional energy meter models
- **Documentation:** Improving guides, examples, and API documentation
- **Testing:** Adding test coverage and validation with different hardware
- **Bug Fixes:** Fixing issues reported by the community
- **Performance:** Optimizing data collection and communication efficiency

### Detailed Guidelines

For comprehensive contribution guidelines, development setup, coding standards, and implementation patterns, please see our [**Contributing Guide**](CONTRIBUTING.md).

### Adding New Counter Support

We especially welcome contributions that add support for new energy counter models. Our library follows a consistent pattern that makes it straightforward to add new devices. Check the [Counter Implementation Guidelines](CONTRIBUTING.md#implementing-new-counter-support) for details.
