import math
import time
from collections.abc import Callable
from threading import Event, Thread

import numpy as np
import pyaudio

from ..core.analysis import (
    from_bytes,
    normalize_samples,
    split_channels,
    to_float,
)
from ..audio.config import AudioConfig


class VolumeMeter:
    """Simple volume meter for audio monitoring."""

    def __init__(self):
        self.peak_raw = [0.0, 0.0]
        self.peak_db = [0.0, 0.0]

    def update(self, samples: np.ndarray) -> None:
        """Update meter with new samples."""
        if samples.ndim == 1:
            samples = samples.reshape(1, -1)

        num_channels = min(samples.shape[0], 2)

        for channel in range(num_channels):
            peak = np.max(np.abs(samples[channel]))
            if peak > self.peak_raw[channel]:
                self.peak_raw[channel] = peak

    def get_peak_db(self) -> list[float]:
        """Get peak levels in dB and reset."""
        for channel in range(2):
            if self.peak_raw[channel] > 0.0:
                self.peak_db[channel] = 20.0 * math.log10(self.peak_raw[channel])
            else:
                self.peak_db[channel] = -120.0  # Silence floor
            self.peak_raw[channel] = 0.0

        return self.peak_db.copy()


class StreamReader:
    """Reads real-time audio streams for glitch detection."""

    def __init__(
        self,
        config: AudioConfig,
        device_id: int | None = None,
        signal_threshold_db: float = -40.0,
    ):
        self.config = config
        self.device_id = device_id
        self.signal_threshold_db = signal_threshold_db

        self._pyaudio: pyaudio.PyAudio | None = None
        self._stream: pyaudio.Stream | None = None
        self._running = False
        self._thread: Thread | None = None

        self.volume_meter = VolumeMeter()

    def open(self) -> None:
        """Open the audio stream."""
        self.config.validate()
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=self.config.pyaudio_format,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input_device_index=self.device_id,
            input=True,
            frames_per_buffer=int(self.config.block_size),
        )

    def close(self) -> None:
        """Close the audio stream."""
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        if self._pyaudio is not None:
            self._pyaudio.terminate()
            self._pyaudio = None

    def start_monitoring(self, callback: Callable[[np.ndarray, int], None], exit_event: Event) -> Thread:
        """Start monitoring audio stream in background thread.

        Raises:
            RuntimeError if stream is not opened.
        """
        if self._stream is None:
            raise RuntimeError("Stream not opened")

        self._running = True
        self._thread = Thread(target=self._monitoring_loop, args=(callback, exit_event))
        self._thread.start()
        return self._thread

    def stop_monitoring(self) -> None:
        """Stop monitoring (pause data processing)."""
        self._running = False

    def resume_monitoring(self) -> None:
        """Resume monitoring."""
        self._running = True

    def _monitoring_loop(self, callback: Callable[[np.ndarray, int], None], exit_event: Event) -> None:
        """Main monitoring loop running in background thread."""
        frame_number = 0

        try:
            while not exit_event.is_set():
                if not self._running:
                    time.sleep(0.1)
                    continue

                try:
                    num_frames = int(self.config.block_size)
                    raw_data = self._stream.read(num_frames)
                    samples = from_bytes(raw_data, self.config.channels, self.config.bit_depth)
                    samples = split_channels(samples, self.config.channels)
                    samples = to_float(samples)

                    # Update volume meter
                    self.volume_meter.update(samples)

                    callback(samples, frame_number)
                    frame_number += self.config.block_size

                except OSError as e:
                    print(f"Audio stream error: {e}")
                    break

        except KeyboardInterrupt:
            pass
        finally:
            self.close()

    def _process_raw_data(self, raw_data: bytes) -> np.ndarray | None:
        """Process raw audio data into samples."""
        # Convert to samples
        samples = from_bytes(raw_data, self.config.channels, self.config.bit_depth)
        samples = split_channels(samples, self.config.channels)
        samples = to_float(samples)

        # Update volume meter
        self.volume_meter.update(samples)

        # Check signal threshold
        peak_db = self.volume_meter.get_peak_db()
        if all(peak < self.signal_threshold_db for peak in peak_db):
            return None

        # Normalize for analysis
        samples = normalize_samples(samples)
        return samples

    def get_volume_db(self) -> list[float]:
        """Get current volume levels in dB."""
        return self.volume_meter.get_peak_db()

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
