from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

from ..core.analysis import calculate_derivative, normalize_samples


def save_waveform_png(
    samples: np.ndarray,
    sample_rate: int,
    frame_offset: int,
    filepath: Path,
    threshold: float = 0.1,
) -> None:
    """Save waveform visualization with derivative analysis as PNG."""
    # Calculate derivative for analysis
    derivative = calculate_derivative(normalize_samples(samples))

    # Create time axes
    duration = samples.shape[1] / sample_rate
    time_axis = np.linspace(0, duration * 1000, samples.shape[1])  # in milliseconds
    # Derivative is one sample shorter due to convolution
    time_axis_deriv = np.linspace(0, duration * 1000, derivative.shape[1])

    if samples.shape[0] == 1:
        # Mono: 2 subplots (waveform + derivative)
        plt.figure(figsize=(12, 8))

        # Waveform
        plt.subplot(2, 1, 1)
        plt.plot(time_axis, samples[0], "b-", linewidth=0.5)
        plt.ylabel("Amplitude")
        plt.title(f"Glitch Block - Frame {frame_offset}")
        plt.grid(True, alpha=0.3)

        # Derivative
        plt.subplot(2, 1, 2)
        plt.plot(time_axis_deriv, derivative[0], "g-", linewidth=0.5)
        plt.axhline(
            y=threshold,
            color="r",
            linestyle="--",
            linewidth=1,
            label=f"Threshold = {threshold}",
        )
        plt.ylabel("Derivative")
        plt.xlabel("Time (ms)")
        plt.legend()
        plt.grid(True, alpha=0.3)

    else:
        # Stereo: 3 subplots (left, right, derivative)
        plt.figure(figsize=(12, 10))

        # Left channel
        plt.subplot(3, 1, 1)
        plt.plot(time_axis, samples[0], "b-", linewidth=0.5)
        plt.ylabel("Left Channel")
        plt.title(f"Glitch Block - Frame {frame_offset}")
        plt.grid(True, alpha=0.3)

        # Right channel
        plt.subplot(3, 1, 2)
        plt.plot(time_axis, samples[1], "r-", linewidth=0.5)
        plt.ylabel("Right Channel")
        plt.grid(True, alpha=0.3)

        # Combined derivative (max across channels for visualization)
        plt.subplot(3, 1, 3)
        combined_derivative = np.max(derivative, axis=0)
        plt.plot(
            time_axis_deriv,
            combined_derivative,
            "g-",
            linewidth=0.5,
            label="Max derivative",
        )
        plt.axhline(
            y=threshold,
            color="r",
            linestyle="--",
            linewidth=1,
            label=f"Threshold = {threshold}",
        )
        plt.ylabel("Derivative")
        plt.xlabel("Time (ms)")
        plt.legend()
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(filepath), dpi=150, bbox_inches="tight")
    plt.close()


def save_glitch_block(
    samples: np.ndarray,
    sample_rate: int,
    frame_offset: int,
    threshold: float,
    output_dir: Path = None,
) -> None:
    """Save audio block containing glitch as WAV file and PNG waveform with derivative analysis."""
    if output_dir is None:
        output_dir = Path("glitch_artifacts")

    output_dir.mkdir(exist_ok=True)

    # Create base filename with timestamp
    timestamp_ms = (frame_offset / sample_rate) * 1000
    base_filename = f"glitch_block_{frame_offset:08d}_{timestamp_ms:.0f}ms"

    # Save WAV file
    wav_filepath = output_dir / f"{base_filename}.wav"
    # Convert samples from (channels, samples) to (samples, channels) for soundfile
    if samples.ndim == 2:
        samples_for_save = samples.T
    else:
        samples_for_save = samples
    sf.write(str(wav_filepath), samples_for_save, sample_rate)

    # Save PNG waveform with derivative analysis
    png_filepath = output_dir / f"{base_filename}.png"
    save_waveform_png(samples, sample_rate, frame_offset, png_filepath, threshold)
