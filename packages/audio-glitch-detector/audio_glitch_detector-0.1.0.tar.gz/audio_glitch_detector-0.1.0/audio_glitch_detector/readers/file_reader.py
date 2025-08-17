from collections.abc import Generator
from pathlib import Path

import numpy as np
import soundfile as sf


class FileReader:
    """Reads audio files and provides samples for glitch detection."""

    def __init__(self, file_path: str, block_size: int, overlap: int = 0):
        self.file_path = Path(file_path)
        self._file: sf.SoundFile | None = None
        self._info: sf._SoundFileInfo | None = None
        self.block_size = block_size
        self.overlap = overlap

    def open(self) -> None:
        """Open the audio file."""
        try:
            self._file = sf.SoundFile(str(self.file_path))
            self._info = sf.info(str(self.file_path))

            if self.overlap == 0:
                self.overlap = int(self._info.samplerate / 1000)  # 1ms default

        except Exception as e:
            raise OSError(f"Failed to open audio file: {e}") from e

    def close(self) -> None:
        """Close the audio file."""
        if self._file is not None:
            self._file.close()
            self._file = None

    @property
    def sample_rate(self) -> int:
        """Get the sample rate of the audio file."""
        if self._info is None:
            raise RuntimeError("File not opened")
        return int(self._info.samplerate)

    @property
    def channels(self) -> int:
        """Get the number of channels."""
        if self._info is None:
            raise RuntimeError("File not opened")
        return self._info.channels

    @property
    def frames(self) -> int:
        """Get total number of frames."""
        if self._info is None:
            raise RuntimeError("File not opened")
        return self._info.frames

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.frames / self.sample_rate

    @property
    def bit_depth(self) -> str:
        """Get bit depth information."""
        if self._info is None:
            raise RuntimeError("File not opened")
        return self._info.subtype_info

    def read_all(self) -> np.ndarray:
        """Read entire file as samples. Return ndarray of samples with shape (channels, samples)"""
        if self._file is None:
            raise RuntimeError("File not opened")

        self._file.seek(0)
        samples = self._file.read()

        if self.channels == 1:
            return samples.reshape(1, -1)
        else:
            return samples.T

    def read_blocks(self) -> Generator[tuple[np.ndarray, int], None, None]:
        """Read file in blocks with overlap. Yields tuple of (samples, frame_offset) where samples has shape (channels, samples)"""
        if self._file is None:
            raise RuntimeError("File not opened")

        current_frame = 0

        for block in sf.blocks(str(self.file_path), blocksize=self.block_size, overlap=self.overlap):
            if self.channels == 1:
                samples = block.reshape(1, -1)
            else:
                samples = block.T

            yield samples, current_frame
            current_frame += self.block_size - self.overlap

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
