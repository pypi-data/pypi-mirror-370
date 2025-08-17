#!/usr/bin/env python3
"""
Basic example of using audio-glitch-detector as a library.
"""

import numpy as np

from audio_glitch_detector import GlitchDetector


def create_test_signal_with_glitch():
    """Create a test sine wave with an artificial glitch."""
    sample_rate = 44100
    duration = 1.0  # 1 second
    frequency = 440  # A4 note

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate clean sine wave
    signal = np.sin(2 * np.pi * frequency * t)

    # Add a glitch at 0.5 seconds (sudden jump)
    glitch_sample = int(0.5 * sample_rate)
    signal[glitch_sample : glitch_sample + 10] += 0.8  # Sharp discontinuity

    return signal, sample_rate


def main():
    print("Audio Glitch Detector - Basic Library Usage Example")
    print("=" * 50)

    # Create test signal
    audio_samples, sample_rate = create_test_signal_with_glitch()
    print(f"Created test signal: {len(audio_samples)} samples at {sample_rate} Hz")

    # Initialize detector
    threshold = 0.1
    detector = GlitchDetector(sample_rate, threshold)
    print(f"Initialized detector with threshold: {threshold}")

    # Detect glitches
    # Note: GlitchDetector expects (channels, samples) format
    if audio_samples.ndim == 1:
        # Convert mono to (1, samples) format
        audio_samples = audio_samples.reshape(1, -1)

    result = detector.detect(audio_samples)

    # Display results
    print("\nDetection Results:")
    print(f"Number of glitches found: {result.total_count}")

    if result.total_count > 0:
        print("Glitch locations:")
        for i, (sample_idx, timestamp_ms) in enumerate(zip(result.sample_indices, result.timestamps_ms)):
            print(f"  {i + 1}. Sample {sample_idx} at {timestamp_ms:.1f} ms")
    else:
        print("No glitches detected. Try lowering the threshold.")


if __name__ == "__main__":
    main()
