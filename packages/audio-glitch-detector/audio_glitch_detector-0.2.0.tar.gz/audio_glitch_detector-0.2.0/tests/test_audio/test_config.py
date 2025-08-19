import pyaudio
import pytest

from audio_glitch_detector.audio.config import AudioConfig


class TestAudioConfig:
    def test_default_values(self):
        config = AudioConfig()
        assert config.sample_rate == 48000
        assert config.channels == 2
        assert config.bit_depth == 16
        assert config.block_size == 1024

    def test_custom_values(self):
        config = AudioConfig(sample_rate=44100, channels=1, bit_depth=32, block_size=512)
        assert config.sample_rate == 44100
        assert config.channels == 1
        assert config.bit_depth == 32
        assert config.block_size == 512

    def test_pyaudio_format_16bit(self):
        config = AudioConfig(bit_depth=16)
        assert config.pyaudio_format == pyaudio.paInt16

    def test_pyaudio_format_32bit(self):
        config = AudioConfig(bit_depth=32)
        assert config.pyaudio_format == pyaudio.paInt32

    def test_pyaudio_format_unsupported(self):
        config = AudioConfig(bit_depth=24)
        with pytest.raises(ValueError, match="Unsupported bit depth"):
            config.pyaudio_format

    def test_sample_width_bytes_16bit(self):
        config = AudioConfig(bit_depth=16)
        assert config.sample_width_bytes == 2

    def test_sample_width_bytes_32bit(self):
        config = AudioConfig(bit_depth=32)
        assert config.sample_width_bytes == 4

    def test_validate_success(self):
        config = AudioConfig()
        config.validate()  # Should not raise

    def test_validate_negative_sample_rate(self):
        config = AudioConfig(sample_rate=-1000)
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            config.validate()

    def test_validate_zero_sample_rate(self):
        config = AudioConfig(sample_rate=0)
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            config.validate()

    def test_validate_invalid_channels(self):
        config = AudioConfig(channels=3)
        with pytest.raises(ValueError, match="Only mono \\(1\\) or stereo \\(2\\) channels supported"):
            config.validate()

    def test_validate_invalid_bit_depth(self):
        config = AudioConfig(bit_depth=24)
        with pytest.raises(ValueError, match="Only 16-bit or 32-bit depth supported"):
            config.validate()

    def test_validate_negative_chunk_size(self):
        config = AudioConfig(block_size=-100)
        with pytest.raises(ValueError, match="Block size must be positive"):
            config.validate()

    def test_validate_zero_chunk_size(self):
        config = AudioConfig(block_size=0)
        with pytest.raises(ValueError, match="Block size must be positive"):
            config.validate()
