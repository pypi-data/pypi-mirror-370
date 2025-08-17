"""Test command-line interface functionality."""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from mhz14a.cli import main
from mhz14a.exceptions import MHZ14AError


class TestCLI:
    """Test command-line interface."""

    def test_help_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test help output."""
        with patch.object(sys, 'argv', ['mhz14a', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert 'MH-Z14A CO₂ sensor command-line interface' in captured.out
        assert 'read' in captured.out
        assert 'sample' in captured.out

    def test_read_command_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test successful read command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor
            mock_sensor.read_co2.return_value = 415

            with patch.object(sys, 'argv', ['mhz14a', '--port', '/dev/test', 'read']):
                main()

        captured = capsys.readouterr()
        assert '415' in captured.out

    def test_read_command_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test read command with sensor error."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor
            mock_sensor.read_co2.side_effect = MHZ14AError("Communication failed")

            with patch.object(sys, 'argv', ['mhz14a', '--port', '/dev/test', 'read']):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert 'Error: Failed to read CO₂: Communication failed' in captured.err

    def test_sample_command_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test sample command with JSON output."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor
            mock_sensor.read_co2.side_effect = [400, 410, 420]

            with patch('time.sleep'):  # Mock sleep to speed up test
                with patch.object(sys, 'argv', [
                    'mhz14a', '--port', '/dev/test', 'sample',
                    '--interval', '1', '--count', '3', '--json'
                ]):
                    main()

        captured = capsys.readouterr()
        output = json.loads(captured.out.strip())

        assert len(output) == 3
        assert output[0]['ppm'] == 400
        assert output[1]['ppm'] == 410
        assert output[2]['ppm'] == 420

        # Check that timestamps are present
        for reading in output:
            assert 'timestamp' in reading
            assert 'ppm' in reading

    def test_sample_command_text(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test sample command with text output."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor
            mock_sensor.read_co2.side_effect = [400, 410]

            with patch('time.sleep'):  # Mock sleep to speed up test
                with patch.object(sys, 'argv', [
                    'mhz14a', '--port', '/dev/test', 'sample',
                    '--interval', '1', '--count', '2'
                ]):
                    main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        assert len(lines) == 2
        assert '400 ppm' in lines[0]
        assert '410 ppm' in lines[1]

    def test_zero_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test zero calibration command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor

            with patch.object(sys, 'argv', ['mhz14a', '--port', '/dev/test', 'zero']):
                main()

        captured = capsys.readouterr()
        assert 'Zero point calibration completed' in captured.out
        mock_sensor.zero_calibrate.assert_called_once()

    def test_span_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test span calibration command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor

            with patch.object(sys, 'argv', [
                'mhz14a', '--port', '/dev/test', 'span', '--ppm', '2000'
            ]):
                main()

        captured = capsys.readouterr()
        assert 'Span calibration completed with 2000 ppm' in captured.out
        mock_sensor.span_calibrate.assert_called_once_with(2000)

    def test_abc_enable_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test ABC enable command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor

            with patch.object(sys, 'argv', [
                'mhz14a', '--port', '/dev/test', 'abc', '--on'
            ]):
                main()

        captured = capsys.readouterr()
        assert 'Automatic Baseline Correction enabled' in captured.out
        mock_sensor.set_abc.assert_called_once_with(True)

    def test_abc_disable_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test ABC disable command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor

            with patch.object(sys, 'argv', [
                'mhz14a', '--port', '/dev/test', 'abc', '--off'
            ]):
                main()

        captured = capsys.readouterr()
        assert 'Automatic Baseline Correction disabled' in captured.out
        mock_sensor.set_abc.assert_called_once_with(False)

    def test_range_command(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test range setting command."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor

            with patch.object(sys, 'argv', [
                'mhz14a', '--port', '/dev/test', 'range', '--max', '5000'
            ]):
                main()

        captured = capsys.readouterr()
        assert 'Measurement range set to 0-5000 ppm' in captured.out
        mock_sensor.set_range.assert_called_once_with(5000)

    def test_no_command_shows_help(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test that running without command shows help."""
        with patch.object(sys, 'argv', ['mhz14a']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert 'MH-Z14A CO₂ sensor command-line interface' in captured.out

    def test_keyboard_interrupt_sample_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test KeyboardInterrupt during sample with JSON output."""
        with patch('mhz14a.cli.MHZ14A') as mock_sensor_class:
            mock_sensor = MagicMock()
            mock_sensor_class.return_value.__enter__.return_value = mock_sensor
            mock_sensor.read_co2.side_effect = [400, KeyboardInterrupt()]

            with patch.object(sys, 'argv', [
                'mhz14a', '--port', '/dev/test', 'sample',
                '--interval', '1', '--count', '5', '--json'
            ]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 130  # 128 + SIGINT

        captured = capsys.readouterr()
        # Should output partial JSON results
        output = json.loads(captured.out.strip())
        assert len(output) == 1
        assert output[0]['ppm'] == 400
