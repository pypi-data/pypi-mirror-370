import pytest

from audio_glitch_detector.readers import FileReader
from audio_glitch_detector.core import GlitchDetector


class TestFileDetection:
    """Integration tests for file-based glitch detection."""

    @pytest.mark.parametrize(
        "expected_glitches,filename",
        [
            (0, "sine_discont_0_mono_440hz.wav"),
            (0, "sine_discont_0_stereo_440_552hz.wav"),
            (2, "sine_discont_2_mono_1khz.wav"),
            (2, "sine_discont_2_stereo_900hz.wav"),
            (4, "sine_discont_4_mono_1khz.wav"),
            (4, "sine_discont_4_stereo_1khz.wav"),
            (5, "sine_discont_5_mono_440hz.wav"),
            (5, "sine_discont_5_stereo_440_552hz.wav"),
            (6, "sine_discont_6_mono_1_1k2hz.wav"),
        ],
    )
    def test_detect_expected_glitches(self, test_files_dir, expected_glitches, filename):
        """Test that detector finds the expected number of glitches in test files."""
        filepath = test_files_dir / filename

        # Skip test if file doesn't exist
        if not filepath.exists():
            pytest.skip(f"Test file {filename} not found")

        with FileReader(str(filepath), block_size=1024) as reader:
            detector = GlitchDetector(reader.sample_rate)

            # Process entire file at once for this test
            samples = reader.read_all()
            result = detector.detect(samples)

            # Assert we found the expected number of glitches
            assert result.total_count == expected_glitches, (
                f"Expected {expected_glitches} glitches in {filename}, but found {result.total_count}"
            )

    def test_block_based_detection_consistency(self, test_files_dir):
        """Test that block-based detection gives same results as full-file detection."""
        filepath = test_files_dir / "sine_discont_2_mono_1khz.wav"

        if not filepath.exists():
            pytest.skip("Test file sine_discont_2_mono.wav not found")

        block_size = 1024
        overlap = 100

        # Full file detection
        with FileReader(str(filepath), 1024) as reader:
            detector = GlitchDetector(reader.sample_rate)
            samples = reader.read_all()
            full_result = detector.detect(samples)

        # Block-based detection
        with FileReader(str(filepath), block_size=block_size, overlap=overlap) as reader:
            detector = GlitchDetector(reader.sample_rate)

            all_glitch_indices = []
            for samples, frame_offset in reader.read_blocks():
                result = detector.detect_with_offset(samples, frame_offset)
                all_glitch_indices.extend(result.sample_indices)

            # Remove duplicates and get final count
            unique_indices = sorted(set(all_glitch_indices))
            block_count = len(unique_indices)

        # Results should be the same (or very close due to overlap handling)
        assert abs(full_result.total_count - block_count) <= 1, (
            f"Full file detection found {full_result.total_count} glitches, "
            f"but block-based detection found {block_count}"
        )
