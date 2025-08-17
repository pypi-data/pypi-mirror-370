from dataclasses import dataclass

import pyaudio


@dataclass
class AudioDevice:
    """Information about an audio device."""

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float

    @property
    def is_input_device(self) -> bool:
        """Check if device supports audio input."""
        return self.max_input_channels > 0


def list_audio_devices() -> list[AudioDevice]:
    """Get list of available audio devices."""
    p = pyaudio.PyAudio()
    devices = []

    try:
        num_devices = p.get_device_count()
        for i in range(num_devices):
            info = p.get_device_info_by_index(i)
            device = AudioDevice(
                index=i,
                name=info["name"],
                max_input_channels=info["maxInputChannels"],
                max_output_channels=info["maxOutputChannels"],
                default_sample_rate=info["defaultSampleRate"],
            )
            devices.append(device)
    finally:
        p.terminate()

    return devices


def print_audio_devices() -> None:
    """Print available audio devices to console."""
    devices = list_audio_devices()
    for device in devices:
        print(f"Device {device.index}: {device.name}")


def get_device_by_index(device_index: int) -> AudioDevice:
    """Get device information by index.

    Raises:
        ValueError: If device index is invalid
    """
    devices = list_audio_devices()
    for device in devices:
        if device.index == device_index:
            return device
    raise ValueError(f"No device found with index {device_index}")
