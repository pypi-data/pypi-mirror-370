import numpy as np


def calculate_derivative(samples: np.ndarray) -> np.ndarray:
    """Calculate the absolute value of the first derivative of audio samples."""
    if samples.ndim == 1:
        samples = samples.reshape(1, -1)

    num_channels = samples.shape[0]
    derivative = np.zeros(samples.shape)
    filter_kernel = np.array([-1, 1])

    for channel in range(num_channels):
        # remove the last sample to match the length of the derivative
        derivative[channel] = np.abs(np.convolve(samples[channel], filter_kernel))[:-1]
        # set the first sample to zero to avoid edge effects
        derivative[channel][0] = 0

    return derivative


def find_glitch_indices(derivative: np.ndarray, threshold: float = 0.5) -> list[list[int]]:
    """Find sample indices where discontinuities exceed threshold."""
    if derivative.ndim == 1:
        derivative = derivative.reshape(1, -1)

    num_channels = derivative.shape[0]
    discontinuities = [[] for _ in range(num_channels)]

    for channel in range(num_channels):
        for index, sample in enumerate(derivative[channel][1:-1]):
            if sample > threshold:
                discontinuities[channel].append(index + 1)

    return discontinuities


def find_optimal_threshold(samples: np.ndarray, percentile: float = 99.5) -> float:
    """
    Automatically determine optimal threshold by analyzing derivative distribution.
    """
    if samples.ndim == 1:
        samples = samples.reshape(1, -1)

    derivative = calculate_derivative(samples)
    all_derivatives = derivative.flatten()

    # Remove zeros and very small values that are just noise
    non_zero_derivatives = all_derivatives[all_derivatives > 1e-6]

    if len(non_zero_derivatives) == 0:
        return 0.1

    base_threshold = np.percentile(non_zero_derivatives, percentile)

    min_threshold = 0.01
    max_threshold = 1.0
    multiplier = 1.1

    threshold = max(base_threshold * multiplier, min_threshold)
    threshold = min(threshold, max_threshold)

    return float(threshold)


def filter_nearby_glitches(discontinuities: list[int], window: int = 50) -> list[int]:
    """Filter out glitch detections that are too close together within a sample window."""
    if not discontinuities:
        return []

    unique_discontinuities = sorted(set(discontinuities))
    filtered = [unique_discontinuities[0]]

    for value in unique_discontinuities[1:]:
        if value - filtered[-1] >= window:
            filtered.append(value)

    return filtered


def normalize_samples(samples: np.ndarray, noise_threshold: float = 0.005) -> np.ndarray:
    """Normalize samples to range [-1.0, 1.0] only if signal is above noise threshold."""
    max_val = np.max(np.abs(samples))
    if max_val < noise_threshold:
        return samples
    return samples / max_val


def to_float(samples: np.ndarray) -> np.ndarray:
    """Convert integer samples to float range [-1.0, 1.0]."""
    info = np.iinfo(samples.dtype)
    # Use the absolute value of min to handle signed integer asymmetry correctly
    return samples.astype(float) / max(abs(info.min), abs(info.max))


def split_channels(samples: np.ndarray, channels: int) -> np.ndarray:
    """Split interleaved samples into separate channels."""
    return np.vstack([samples[i::channels] for i in range(channels)])


def from_bytes(data: bytes, channels: int, bit_depth: int) -> np.ndarray:
    """Convert raw bytes to NumPy array of samples."""
    dtype = np.int16 if bit_depth == 16 else np.int32
    return np.frombuffer(data, dtype=dtype)
