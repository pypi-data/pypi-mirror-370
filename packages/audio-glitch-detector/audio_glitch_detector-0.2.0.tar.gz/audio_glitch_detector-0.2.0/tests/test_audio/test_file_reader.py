import pytest

from audio_glitch_detector.readers.file_reader import FileReader


class TestFileReader:
    def test_context_manager(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"

        with FileReader(str(file_path), 1024) as reader:
            assert reader._file is not None
            assert reader._info is not None

        # Should be closed after context
        assert reader._file is None

    def test_file_properties(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"

        with FileReader(str(file_path), 1024) as reader:
            assert reader.sample_rate > 0
            assert reader.channels > 0
            assert reader.frames > 0
            assert reader.duration_seconds > 0

    def test_mono_file_reading(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"

        with FileReader(str(file_path), 1024) as reader:
            assert reader.channels == 1
            samples = reader.read_all()
            assert samples.shape[0] == 1  # Should have 1 channel
            assert samples.shape[1] > 0  # Should have samples

    def test_stereo_file_reading(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_stereo_900hz.wav"

        with FileReader(str(file_path), 1024) as reader:
            assert reader.channels == 2
            samples = reader.read_all()
            assert samples.shape[0] == 2  # Should have 2 channels
            assert samples.shape[1] > 0  # Should have samples

    def test_block_reading(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"

        with FileReader(str(file_path), block_size=1024) as reader:
            blocks = list(reader.read_blocks())

            assert len(blocks) > 0
            for samples, frame_offset in blocks:
                assert samples.shape[0] == reader.channels
                assert isinstance(frame_offset, int)
                assert frame_offset >= 0

    def test_file_not_found(self):
        with pytest.raises(IOError):
            with FileReader("nonexistent_file.wav", 1024) as _:
                pass

    def test_runtime_error_when_not_opened(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"
        reader = FileReader(str(file_path), 1024)

        with pytest.raises(RuntimeError):
            reader.sample_rate

        with pytest.raises(RuntimeError):
            reader.channels

        with pytest.raises(RuntimeError):
            reader.frames

        with pytest.raises(RuntimeError):
            reader.read_all()

        with pytest.raises(RuntimeError):
            list(reader.read_blocks())

    def test_custom_block_size_and_overlap(self, test_files_dir):
        file_path = test_files_dir / "sine_discont_2_mono_1khz.wav"

        with FileReader(str(file_path), block_size=512, overlap=64) as reader:
            assert reader.block_size == 512
            assert reader.overlap == 64

            blocks = list(reader.read_blocks())
            assert len(blocks) > 0
