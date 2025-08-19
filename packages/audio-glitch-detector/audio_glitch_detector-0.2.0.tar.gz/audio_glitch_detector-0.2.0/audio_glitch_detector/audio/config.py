from dataclasses import dataclass

import pyaudio


@dataclass
class AudioConfig:
    """Audio configuration for recording and processing."""

    sample_rate: int = 48000
    channels: int = 2
    bit_depth: int = 16
    block_size: int = 1024

    @property
    def pyaudio_format(self) -> int:
        """Get the PyAudio format constant for this bit depth."""
        if self.bit_depth == 16:
            return pyaudio.paInt16
        elif self.bit_depth == 32:
            return pyaudio.paInt32
        else:
            raise ValueError(f"Unsupported bit depth: {self.bit_depth}")

    @property
    def sample_width_bytes(self) -> int:
        """Get sample width in bytes."""
        return self.bit_depth // 8

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels not in (1, 2):
            raise ValueError("Only mono (1) or stereo (2) channels supported")
        if self.bit_depth not in (16, 32):
            raise ValueError("Only 16-bit or 32-bit depth supported")
        if self.block_size <= 0:
            raise ValueError("Block size must be positive")
