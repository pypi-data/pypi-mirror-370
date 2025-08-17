from datetime import timedelta

from audio_glitch_detector.utils.time_utils import (
    format_elapsed_time,
    format_time,
    format_time_string,
    time_to_milliseconds,
)


class TestTimeToMilliseconds:
    def test_basic_conversion(self):
        sample_rate = 48000
        frame_number = 48000  # 1 second worth of samples
        result = time_to_milliseconds(frame_number, sample_rate)
        assert result == 1000.0

    def test_half_second(self):
        sample_rate = 48000
        frame_number = 24000  # 0.5 seconds
        result = time_to_milliseconds(frame_number, sample_rate)
        assert result == 500.0

    def test_zero_frame(self):
        sample_rate = 48000
        frame_number = 0
        result = time_to_milliseconds(frame_number, sample_rate)
        assert result == 0.0

    def test_different_sample_rates(self):
        frame_number = 44100  # 1 second at 44.1kHz
        result = time_to_milliseconds(frame_number, 44100)
        assert result == 1000.0


class TestFormatTime:
    def test_basic_formatting(self):
        ms = 1500.0  # 1.5 seconds
        result = format_time(ms)
        assert isinstance(result, timedelta)
        assert result.total_seconds() == 1.5

    def test_zero_time(self):
        ms = 0.0
        result = format_time(ms)
        assert result.total_seconds() == 0.0

    def test_large_time(self):
        ms = 3661000.0  # 1 hour, 1 minute, 1 second
        result = format_time(ms)
        assert result.total_seconds() == 3661.0


class TestFormatTimeString:
    def test_basic_string_format(self):
        ms = 1500.0  # 1.5 seconds
        result = format_time_string(ms)
        assert result == "00:00:01.500"

    def test_zero_time_string(self):
        ms = 0.0
        result = format_time_string(ms)
        assert result == "00:00:00.000"

    def test_one_hour_format(self):
        ms = 3661500.0  # 1:01:01.500
        result = format_time_string(ms)
        assert result == "01:01:01.500"

    def test_minutes_and_seconds(self):
        ms = 75200.0  # 1:15.200
        result = format_time_string(ms)
        assert result == "00:01:15.200"

    def test_milliseconds_precision(self):
        ms = 1234.567
        result = format_time_string(ms)
        assert result == "00:00:01.234"  # Should truncate to 3 decimal places


class TestFormatElapsedTime:
    def test_basic_elapsed_format(self):
        seconds = 65.0  # 1 minute 5 seconds
        result = format_elapsed_time(seconds)
        assert result == "00:01:05"

    def test_zero_elapsed(self):
        seconds = 0.0
        result = format_elapsed_time(seconds)
        assert result == "00:00:00"

    def test_one_hour_elapsed(self):
        seconds = 3661.0  # 1:01:01
        result = format_elapsed_time(seconds)
        assert result == "01:01:01"

    def test_fractional_seconds_truncated(self):
        seconds = 65.7  # Should truncate to 65
        result = format_elapsed_time(seconds)
        assert result == "00:01:05"

    def test_large_time_elapsed(self):
        seconds = 7323.0  # 2:02:03
        result = format_elapsed_time(seconds)
        assert result == "02:02:03"
