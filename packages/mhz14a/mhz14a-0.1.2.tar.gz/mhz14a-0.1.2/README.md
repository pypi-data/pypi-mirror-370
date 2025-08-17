# MH-Z14A Python Library

[![CI](https://github.com/oaslananka/mhz14a/actions/workflows/ci.yml/badge.svg)](https://github.com/oaslananka/mhz14a/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mhz14a.svg)](https://pypi.org/project/mhz14a/)
[![Python versions](https://img.shields.io/pypi/pyversions/mhz14a.svg)](https://pypi.org/project/mhz14a/)

Python library and command-line interface for the MH-Z14A CO₂ sensor.

## Features

- Pure Python implementation with minimal dependencies (only `pyserial`)
- Type-safe with full type annotations
- Command-line interface for easy integration
- Context manager support
- Comprehensive error handling with retry logic
- Supports all sensor features: reading, calibration, ABC, range setting

## Installation

```bash
pip install mhz14a
```

## Quick Start

### Python Library

```python
from mhz14a import MHZ14A

# Using context manager (recommended)
with MHZ14A('/dev/mhz14a') as sensor:
    ppm = sensor.read_co2()
    print(f"CO₂: {ppm} ppm")

# Manual connection management
sensor = MHZ14A('/dev/mhz14a')
sensor._connect()
try:
    ppm = sensor.read_co2()
    print(f"CO₂: {ppm} ppm")
finally:
    sensor._disconnect()
```

### Command-Line Interface

```bash
# Read CO₂ concentration
mhz14a --port /dev/mhz14a read

# Sample readings every 5 seconds, 10 times
mhz14a --port /dev/mhz14a sample --interval 5 --count 10

# Sample with JSON output
mhz14a --port /dev/mhz14a sample --interval 1 --count 5 --json

# Zero point calibration (in fresh air, 400 ppm)
mhz14a --port /dev/mhz14a zero

# Span calibration with known concentration
mhz14a --port /dev/mhz14a span --ppm 2000

# Enable/disable Automatic Baseline Correction
mhz14a --port /dev/mhz14a abc --on
mhz14a --port /dev/mhz14a abc --off

# Set measurement range
mhz14a --port /dev/mhz14a range --max 5000
```

## Raspberry Pi Setup

### Hardware Connection

Connect the MH-Z14A sensor to your Raspberry Pi using a USB-to-TTL converter (e.g., CH340):

- MH-Z14A VIN → 5V (or 3.3V depending on sensor version)
- MH-Z14A GND → GND
- MH-Z14A TXD → USB-TTL RXD
- MH-Z14A RXD → USB-TTL TXD

### udev Rule Setup

Create a persistent device name for your sensor:

1. Copy the provided udev rule:
   ```bash
   sudo cp extras/99-mhz14a.rules /etc/udev/rules.d/
   ```

2. Reload udev rules:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

3. Add your user to the `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   ```

4. Log out and log back in for group changes to take effect.

The sensor will now be available as `/dev/mhz14a` instead of `/dev/ttyUSB0`.

### udev Rule Content

The `extras/99-mhz14a.rules` file contains:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="mhz14a", MODE="0660", GROUP="dialout"
```

## Calibration

### Zero Point Calibration

⚠️ **Important**: Only perform zero calibration in fresh outdoor air (approximately 400 ppm CO₂):

1. Power on the sensor and wait at least 20 minutes for stabilization
2. Ensure the sensor is in fresh air (outdoors or well-ventilated area)
3. Run calibration:
   ```bash
   mhz14a --port /dev/mhz14a zero
   ```

### Span Calibration

For span calibration, you need a known CO₂ concentration:

```bash
mhz14a --port /dev/mhz14a span --ppm 2000
```

### Automatic Baseline Correction (ABC)

ABC automatically adjusts the zero point based on the assumption that the lowest CO₂ reading in a 24-hour period represents fresh air (400 ppm).

- **Enable ABC** (default, suitable for most applications):
  ```bash
  mhz14a --port /dev/mhz14a abc --on
  ```

- **Disable ABC** (for continuous high CO₂ environments):
  ```bash
  mhz14a --port /dev/mhz14a abc --off
  ```

## Measurement Ranges

The sensor supports three measurement ranges:

- **2000 ppm** (0-2000 ppm): Higher resolution, suitable for indoor air quality
- **5000 ppm** (0-5000 ppm): Balanced range for most applications
- **10000 ppm** (0-10000 ppm): Maximum range for industrial applications

```bash
mhz14a --port /dev/mhz14a range --max 2000
mhz14a --port /dev/mhz14a range --max 5000
mhz14a --port /dev/mhz14a range --max 10000
```

## Python API Reference

### MHZ14A Class

```python
class MHZ14A:
    def __init__(self, port: str, timeout: float = 1.0) -> None:
        """Initialize sensor with port and timeout."""
    
    def read_co2(self) -> int:
        """Read CO₂ concentration in ppm."""
    
    def zero_calibrate(self) -> None:
        """Perform zero point calibration (400 ppm fresh air)."""
    
    def span_calibrate(self, ppm: int) -> None:
        """Perform span calibration with known concentration."""
    
    def set_abc(self, enable: bool) -> None:
        """Enable or disable Automatic Baseline Correction."""
    
    def set_range(self, max_ppm: int) -> None:
        """Set measurement range (2000, 5000, or 10000 ppm)."""
```

### Error Handling

All sensor operations can raise `MHZ14AError` exceptions:

```python
from mhz14a import MHZ14A, MHZ14AError

try:
    with MHZ14A('/dev/mhz14a') as sensor:
        ppm = sensor.read_co2()
        print(f"CO₂: {ppm} ppm")
except MHZ14AError as e:
    print(f"Sensor error: {e}")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- MH-Z14A sensor documentation and protocol specifications
- Python serial communication community
