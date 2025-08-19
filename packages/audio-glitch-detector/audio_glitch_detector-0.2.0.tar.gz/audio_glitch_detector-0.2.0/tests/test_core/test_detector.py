from audio_glitch_detector.core.detector import DetectionResult, GlitchDetector


class TestGlitchDetector:
    def test_initialization(self, sample_rate):
        detector = GlitchDetector(sample_rate, threshold=0.1)
        assert detector.sample_rate == sample_rate
        assert detector.threshold == 0.1

    def test_clean_signal_detection(self, mono_sine_wave, sample_rate):
        detector = GlitchDetector(sample_rate, threshold=0.5)
        result = detector.detect(mono_sine_wave)

        assert isinstance(result, DetectionResult)
        assert result.total_count == 0
        assert len(result.sample_indices) == 0
        assert len(result.timestamps_ms) == 0

    def test_glitch_detection(self, sine_with_discontinuity, sample_rate):
        detector = GlitchDetector(sample_rate, threshold=0.1)
        result = detector.detect(sine_with_discontinuity)

        assert result.total_count > 0
        assert len(result.sample_indices) == result.total_count
        assert len(result.timestamps_ms) == result.total_count

        # Check timestamp calculation
        expected_time_ms = (result.sample_indices[0] / sample_rate) * 1000
        assert abs(result.timestamps_ms[0] - expected_time_ms) < 0.01

    def test_stereo_detection(self, stereo_sine_wave, sample_rate):
        # Add discontinuity to one channel
        stereo_with_glitch = stereo_sine_wave.copy()
        stereo_with_glitch[0, len(stereo_with_glitch[0]) // 2] = 1.0

        detector = GlitchDetector(sample_rate, threshold=0.1)
        result = detector.detect(stereo_with_glitch)

        assert result.total_count > 0

    def test_threshold_sensitivity(self, sine_with_discontinuity, sample_rate):
        low_detector = GlitchDetector(sample_rate, threshold=0.01)
        high_detector = GlitchDetector(sample_rate, threshold=1.0)

        low_result = low_detector.detect(sine_with_discontinuity)
        high_result = high_detector.detect(sine_with_discontinuity)

        # Lower threshold should detect more or equal glitches
        assert low_result.total_count >= high_result.total_count

    def test_stream_detection_with_offset(self, mono_sine_wave, sample_rate):
        detector = GlitchDetector(sample_rate, threshold=0.1)
        current_frame = 1000

        # Add a glitch at the beginning
        glitchy_wave = mono_sine_wave.copy()
        glitchy_wave[10] = 1.0

        result = detector.detect_with_offset(glitchy_wave, current_frame)

        if result.total_count > 0:
            # Sample indices should be offset by current_frame
            assert all(idx >= current_frame for idx in result.sample_indices)

    def test_sample_to_milliseconds_conversion(self, sample_rate):
        detector = GlitchDetector(sample_rate, threshold=0.1)

        # Test conversion
        sample_index = sample_rate  # 1 second worth of samples
        expected_ms = 1000.0  # 1 second = 1000ms

        result_ms = detector._sample_to_milliseconds(sample_index)
        assert abs(result_ms - expected_ms) < 0.01


class TestDetectionResult:
    def test_detection_result_creation(self):
        indices = [100, 200, 300]
        timestamps = [2.08, 4.17, 6.25]
        count = 3
        threshold = 0.1

        result = DetectionResult(
            sample_indices=indices,
            timestamps_ms=timestamps,
            total_count=count,
            threshold=threshold,
        )

        assert result.sample_indices == indices
        assert result.timestamps_ms == timestamps
        assert result.total_count == count
        assert result.threshold == threshold

    def test_empty_detection_result(self):
        result = DetectionResult(sample_indices=[], timestamps_ms=[], total_count=0, threshold=0)

        assert len(result.sample_indices) == 0
        assert len(result.timestamps_ms) == 0
        assert result.total_count == 0
        assert result.threshold == 0.0
