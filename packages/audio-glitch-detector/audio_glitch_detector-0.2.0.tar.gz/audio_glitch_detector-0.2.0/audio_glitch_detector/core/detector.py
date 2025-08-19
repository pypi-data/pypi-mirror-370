from dataclasses import dataclass

import numpy as np

from .analysis import (
    calculate_derivative,
    filter_nearby_glitches,
    find_glitch_indices,
    find_optimal_threshold,
    normalize_samples,
)


@dataclass
class DetectionResult:
    """Result of glitch detection containing timestamps and sample indices."""

    sample_indices: list[int]
    timestamps_ms: list[float]
    total_count: int
    threshold: float
    auto_threshold: bool = False


class GlitchDetector:
    """Detects audio glitches in sinusoidal signals.

    This detector works by analyzing the first derivative of audio signals
    to identify sudden discontinuities that indicate glitches in otherwise continuous signals.
    Threshold should be set so it filters out minor fluctuations that are not considered glitches.
    """

    def __init__(self, sample_rate: int, threshold: float = 0.0):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.auto_threshold = False

    def detect(self, samples: np.ndarray) -> DetectionResult:
        """Detect glitches in audio samples."""

        normalized_samples = normalize_samples(samples)

        threshold = self.threshold

        if self.threshold == 0.0:
            self.auto_threshold = True
            threshold = find_optimal_threshold(normalized_samples)

        derivative = calculate_derivative(normalized_samples)

        discontinuities_per_channel = find_glitch_indices(derivative, threshold)

        # Combine all channels and remove duplicates
        all_discontinuities = []
        for channel_discontinuities in discontinuities_per_channel:
            all_discontinuities.extend(channel_discontinuities)

        filtered_discontinuities = filter_nearby_glitches(all_discontinuities)
        timestamps = [self._sample_to_milliseconds(idx) for idx in filtered_discontinuities]

        return DetectionResult(
            sample_indices=filtered_discontinuities,
            timestamps_ms=timestamps,
            total_count=len(filtered_discontinuities),
            threshold=threshold,
            auto_threshold=self.auto_threshold,
        )

    def detect_with_offset(self, samples: np.ndarray, frame_offset: int) -> DetectionResult:
        """Detect glitches in samples with absolute frame positioning."""
        result = self.detect(samples)

        # Convert relative indices to absolute
        absolute_indices = [idx + frame_offset for idx in result.sample_indices]
        absolute_timestamps = [self._sample_to_milliseconds(idx) for idx in absolute_indices]

        return DetectionResult(
            sample_indices=absolute_indices,
            timestamps_ms=absolute_timestamps,
            total_count=result.total_count,
            threshold=result.threshold,
            auto_threshold=result.auto_threshold,
        )

    def _sample_to_milliseconds(self, sample_index: int) -> float:
        """Convert sample index to milliseconds."""
        return (sample_index / self.sample_rate) * 1000.0
