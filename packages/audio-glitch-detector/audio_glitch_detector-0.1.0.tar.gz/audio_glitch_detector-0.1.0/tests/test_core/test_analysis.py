import numpy as np

from audio_glitch_detector.core.analysis import (
    calculate_derivative,
    filter_nearby_glitches,
    find_glitch_indices,
    from_bytes,
    normalize_samples,
    split_channels,
    to_float,
)


class TestCalculateDerivative:
    def test_mono_signal(self, mono_sine_wave):
        derivative = calculate_derivative(mono_sine_wave)
        assert derivative.shape == (1, len(mono_sine_wave))
        assert np.all(derivative >= 0)  # Should be absolute values

    def test_stereo_signal(self, stereo_sine_wave):
        derivative = calculate_derivative(stereo_sine_wave)
        assert derivative.shape == stereo_sine_wave.shape
        assert np.all(derivative >= 0)

    def test_discontinuity_detection(self, sine_with_discontinuity):
        derivative = calculate_derivative(sine_with_discontinuity)
        # Should have high derivative at discontinuity point
        discontinuity_point = len(sine_with_discontinuity) // 2
        assert derivative[0, discontinuity_point] > 0.5


class TestFindGlitchIndices:
    def test_no_discontinuities(self, mono_sine_wave):
        derivative = calculate_derivative(mono_sine_wave)
        discontinuities = find_glitch_indices(derivative, threshold=0.5)
        assert len(discontinuities) == 1  # One channel
        assert len(discontinuities[0]) == 0  # No discontinuities

    def test_with_discontinuity(self, sine_with_discontinuity):
        derivative = calculate_derivative(sine_with_discontinuity)
        discontinuities = find_glitch_indices(derivative, threshold=0.1)
        assert len(discontinuities) == 1
        assert len(discontinuities[0]) > 0  # Should find discontinuity

    def test_threshold_sensitivity(self, sine_with_discontinuity):
        derivative = calculate_derivative(sine_with_discontinuity)

        low_threshold = find_glitch_indices(derivative, threshold=0.1)
        high_threshold = find_glitch_indices(derivative, threshold=1.0)

        # Lower threshold should find more discontinuities
        assert len(low_threshold[0]) >= len(high_threshold[0])


class TestFilterNearbyGlitches:
    def test_empty_list(self):
        result = filter_nearby_glitches([])
        assert result == []

    def test_no_duplicates_needed(self):
        discontinuities = [100, 200, 300]
        result = filter_nearby_glitches(discontinuities, window=10)
        assert result == discontinuities

    def test_remove_close_duplicates(self):
        discontinuities = [100, 105, 107, 200]
        result = filter_nearby_glitches(discontinuities, window=10)
        assert result == [100, 200]

    def test_custom_window_size(self):
        discontinuities = [100, 110, 125, 200]
        result = filter_nearby_glitches(discontinuities, window=20)
        assert result == [100, 125, 200]


class TestNormalizeSamples:
    def test_normalize_range(self):
        samples = np.array([[-2.0, -1.0, 0.0, 1.0, 2.0]])
        normalized = normalize_samples(samples)
        assert np.max(np.abs(normalized)) == 1.0

    def test_preserve_zero(self):
        samples = np.zeros((1, 100))
        normalized = normalize_samples(samples)
        assert np.all(normalized == 0.0)


class TestConvertToFloat:
    def test_int16_conversion(self):
        samples = np.array([0, 16384, 32767, -16384, -32768], dtype=np.int16)
        result = to_float(samples)
        assert result.dtype == np.float64
        assert np.max(result) <= 1.0
        assert np.min(result) >= -1.0

    def test_int32_conversion(self):
        max_int32 = 2**31 - 1
        samples = np.array(
            [0, max_int32 // 2, max_int32, -max_int32 // 2, -max_int32 - 1],
            dtype=np.int32,
        )
        result = to_float(samples)
        assert result.dtype == np.float64
        assert np.max(result) <= 1.0
        assert np.min(result) >= -1.0


class TestSplitChannels:
    def test_mono_split(self):
        samples = np.array([1, 2, 3, 4, 5])
        result = split_channels(samples, channels=1)
        assert result.shape == (1, 5)
        assert np.array_equal(result[0], samples)

    def test_stereo_split(self):
        interleaved = np.array([1, 2, 3, 4, 5, 6])  # L, R, L, R, L, R
        result = split_channels(interleaved, channels=2)
        assert result.shape == (2, 3)
        assert np.array_equal(result[0], [1, 3, 5])  # Left channel
        assert np.array_equal(result[1], [2, 4, 6])  # Right channel


class TestSamplesFromBytes:
    def test_int16_from_bytes(self):
        # Create test data: two int16 samples
        data = np.array([1000, -1000], dtype=np.int16).tobytes()
        result = from_bytes(data, channels=1, bit_depth=16)
        assert result.dtype == np.int16
        assert len(result) == 2
        assert result[0] == 1000
        assert result[1] == -1000

    def test_int32_from_bytes(self):
        # Create test data: two int32 samples
        data = np.array([100000, -100000], dtype=np.int32).tobytes()
        result = from_bytes(data, channels=1, bit_depth=32)
        assert result.dtype == np.int32
        assert len(result) == 2
        assert result[0] == 100000
        assert result[1] == -100000
