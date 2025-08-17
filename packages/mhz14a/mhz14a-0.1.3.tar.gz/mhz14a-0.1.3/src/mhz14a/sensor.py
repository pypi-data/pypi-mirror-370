"""MH-Z14A CO₂ sensor driver implementation."""

import time
from typing import Final, Optional

import serial

from .exceptions import MHZ14AError

# Protocol constants
FRAME_SIZE: Final[int] = 9
RESPONSE_SIZE: Final[int] = 9
HEADER: Final[int] = 0xFF

# Command bytes
CMD_READ_CO2: Final[int] = 0x86
CMD_ZERO_CALIBRATE: Final[int] = 0x87
CMD_SPAN_CALIBRATE: Final[int] = 0x88
CMD_SET_AUTO_CALIBRATION: Final[int] = 0x79
CMD_SET_RANGE: Final[int] = 0x99

# Range values
RANGE_2000: Final[int] = 2000
RANGE_5000: Final[int] = 5000
RANGE_10000: Final[int] = 10000
VALID_RANGES: Final[tuple[int, ...]] = (RANGE_2000, RANGE_5000, RANGE_10000)


def _checksum(frame8: bytes) -> int:
    """Calculate checksum for 8-byte frame.

    Args:
        frame8: First 8 bytes of the frame

    Returns:
        Calculated checksum byte

    Example:
        >>> _checksum(bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00]))
        121
    """
    return (256 - sum(frame8[1:8])) & 0xFF


def _make_command(cmd: int, data: tuple[int, ...] = ()) -> bytes:
    """Create a 9-byte command frame.

    Args:
        cmd: Command byte
        data: Additional data bytes (up to 5 bytes)

    Returns:
        Complete 9-byte command frame with checksum
    """
    if len(data) > 5:
        raise ValueError("Data too long, max 5 bytes")

    frame8 = bytes([HEADER, 0x01, cmd] + list(data) + [0x00] * (5 - len(data)))
    checksum = _checksum(frame8)
    return frame8 + bytes([checksum])


class MHZ14A:
    """MH-Z14A CO₂ sensor driver.

    This class provides an interface to communicate with the MH-Z14A CO₂ sensor
    over UART using the serial protocol.

    Args:
        port: Serial port path (e.g., '/dev/ttyUSB0' or '/dev/mhz14a')
        timeout: Serial communication timeout in seconds

    Example:
        >>> sensor = MHZ14A('/dev/mhz14a')
        >>> co2_ppm = sensor.read_co2()
        >>> print(f"CO₂: {co2_ppm} ppm")
        CO₂: 415 ppm
    """

    def __init__(self, port: str, timeout: float = 1.0) -> None:
        """Initialize MH-Z14A sensor.

        Args:
            port: Serial port path
            timeout: Communication timeout in seconds
        """
        self.port = port
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None

    def __enter__(self) -> "MHZ14A":
        """Context manager entry."""
        self._connect()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit."""
        self._disconnect()

    def _connect(self) -> None:
        """Establish serial connection."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
        except (serial.SerialException, OSError) as e:
            raise MHZ14AError(f"Failed to open serial port {self.port}: {e}") from e

    def _disconnect(self) -> None:
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _write_command(self, command: bytes) -> None:
        """Write command to sensor with retry logic.

        Args:
            command: 9-byte command to send
        """
        if not self.ser or not self.ser.is_open:
            raise MHZ14AError("Serial connection not established")

        for attempt in range(3):  # Original + 2 retries
            try:
                written = self.ser.write(command)
                if written != len(command):
                    raise MHZ14AError(
                        f"Partial write: {written}/{len(command)} bytes"
                    )
                self.ser.flush()
                return
            except (serial.SerialTimeoutException, serial.SerialException, OSError) as e:
                if attempt == 2:  # Last attempt
                    raise MHZ14AError(f"Write failed after 3 attempts: {e}") from e
                time.sleep(0.1)  # Short delay before retry

    def _read_response(self) -> bytes:
        """Read 9-byte response from sensor with retry logic.

        Returns:
            9-byte response frame
        """
        if not self.ser or not self.ser.is_open:
            raise MHZ14AError("Serial connection not established")

        for attempt in range(3):  # Original + 2 retries
            try:
                response = self.ser.read(RESPONSE_SIZE)
                if len(response) != RESPONSE_SIZE:
                    raise MHZ14AError(
                        f"Incomplete response: {len(response)}/{RESPONSE_SIZE} bytes"
                    )
                return response
            except (serial.SerialTimeoutException, serial.SerialException, OSError) as e:
                if attempt == 2:  # Last attempt
                    raise MHZ14AError(f"Read failed after 3 attempts: {e}") from e
                time.sleep(0.1)  # Short delay before retry

        # This line should never be reached, but mypy needs it
        raise MHZ14AError("Unexpected error in _read_response")

    def _validate_response(self, response: bytes, expected_cmd: int) -> None:
        """Validate response frame format and checksum.

        Args:
            response: 9-byte response to validate
            expected_cmd: Expected command byte in response
        """
        if len(response) != RESPONSE_SIZE:
            raise MHZ14AError(f"Invalid response length: {len(response)}")

        if response[0] != HEADER:
            raise MHZ14AError(f"Invalid header: 0x{response[0]:02X}")

        if response[1] != expected_cmd:
            raise MHZ14AError(
                f"Invalid command in response: 0x{response[1]:02X}, "
                f"expected: 0x{expected_cmd:02X}"
            )

        calculated_checksum = _checksum(response[:8])
        received_checksum = response[8]
        if calculated_checksum != received_checksum:
            raise MHZ14AError(
                f"Checksum mismatch: calculated=0x{calculated_checksum:02X}, "
                f"received=0x{received_checksum:02X}"
            )

    def read_co2(self) -> int:
        """Read CO₂ concentration in ppm.

        Returns:
            CO₂ concentration in parts per million (ppm)

        Raises:
            MHZ14AError: If communication fails or response is invalid

        Example:
            >>> sensor = MHZ14A('/dev/mhz14a')
            >>> with sensor:
            ...     ppm = sensor.read_co2()
            ...     print(f"CO₂: {ppm} ppm")
            CO₂: 415 ppm
        """
        if not self.ser:
            self._connect()

        command = _make_command(CMD_READ_CO2)
        self._write_command(command)
        response = self._read_response()
        self._validate_response(response, CMD_READ_CO2)

        # Extract ppm value from bytes 2 and 3 (high and low bytes)
        high_byte = response[2]
        low_byte = response[3]
        ppm = high_byte * 256 + low_byte

        return ppm

    def zero_calibrate(self) -> None:
        """Perform zero point calibration.

        WARNING: Only perform this calibration in fresh air (400 ppm CO₂)
        after the sensor has been powered on for at least 20 minutes.

        Raises:
            MHZ14AError: If communication fails

        Example:
            >>> sensor = MHZ14A('/dev/mhz14a')
            >>> with sensor:
            ...     sensor.zero_calibrate()
            ...     print("Zero calibration completed")
            Zero calibration completed
        """
        if not self.ser:
            self._connect()

        command = _make_command(CMD_ZERO_CALIBRATE)
        self._write_command(command)
        response = self._read_response()
        self._validate_response(response, CMD_ZERO_CALIBRATE)

    def span_calibrate(self, ppm: int) -> None:
        """Perform span calibration with known CO₂ concentration.

        Args:
            ppm: Known CO₂ concentration for calibration

        Raises:
            MHZ14AError: If communication fails
            ValueError: If ppm is out of valid range

        Example:
            >>> sensor = MHZ14A('/dev/mhz14a')
            >>> with sensor:
            ...     sensor.span_calibrate(2000)  # Calibrate with 2000 ppm CO₂
            ...     print("Span calibration completed")
            Span calibration completed
        """
        if not (0 <= ppm <= 10000):
            raise ValueError(f"Invalid ppm value: {ppm}, must be 0-10000")

        if not self.ser:
            self._connect()

        high_byte = (ppm >> 8) & 0xFF
        low_byte = ppm & 0xFF
        command = _make_command(CMD_SPAN_CALIBRATE, (high_byte, low_byte))
        self._write_command(command)
        response = self._read_response()
        self._validate_response(response, CMD_SPAN_CALIBRATE)

    def set_abc(self, enable: bool) -> None:
        """Enable or disable Automatic Baseline Correction (ABC).

        ABC automatically adjusts the sensor's zero point based on the assumption
        that the lowest CO₂ reading in a 24-hour period represents fresh air (400 ppm).

        Args:
            enable: True to enable ABC, False to disable

        Raises:
            MHZ14AError: If communication fails

        Example:
            >>> sensor = MHZ14A('/dev/mhz14a')
            >>> with sensor:
            ...     sensor.set_abc(True)  # Enable ABC
            ...     print("ABC enabled")
            ABC enabled
        """
        if not self.ser:
            self._connect()

        abc_value = 0xA0 if enable else 0x00
        command = _make_command(CMD_SET_AUTO_CALIBRATION, (abc_value,))
        self._write_command(command)
        response = self._read_response()
        self._validate_response(response, CMD_SET_AUTO_CALIBRATION)

    def set_range(self, max_ppm: int) -> None:
        """Set measurement range.

        Args:
            max_ppm: Maximum measurement range (2000, 5000, or 10000 ppm)

        Raises:
            MHZ14AError: If communication fails
            ValueError: If max_ppm is not a valid range

        Example:
            >>> sensor = MHZ14A('/dev/mhz14a')
            >>> with sensor:
            ...     sensor.set_range(5000)  # Set range to 0-5000 ppm
            ...     print("Range set to 5000 ppm")
            Range set to 5000 ppm
        """
        if max_ppm not in VALID_RANGES:
            raise ValueError(
                f"Invalid range: {max_ppm}, must be one of {VALID_RANGES}"
            )

        if not self.ser:
            self._connect()

        high_byte = (max_ppm >> 8) & 0xFF
        low_byte = max_ppm & 0xFF
        command = _make_command(CMD_SET_RANGE, (high_byte, low_byte))
        self._write_command(command)
        response = self._read_response()
        self._validate_response(response, CMD_SET_RANGE)
