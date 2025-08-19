import math
import sys
from pathlib import Path

from tqdm import tqdm

from .audio import BoundedGlitchQueue, save_glitch_block
from .readers import FileReader
from .core import GlitchDetector
from .tui import ConsoleOutput
from .utils import format_time_string


def run_file_mode(
    filename: str,
    threshold: float,
    block_size: int,
    save_blocks: int | None,
    output: ConsoleOutput,
) -> None:
    """Run glitch detection on a file using block-based processing with block overlap."""
    try:
        with FileReader(filename, block_size=1, overlap=0) as temp_reader:
            sample_rate = temp_reader.sample_rate
            channels = temp_reader.channels
            duration = temp_reader.duration_seconds
            total_frames = temp_reader.frames
            bit_depth = temp_reader.bit_depth

        overlap = int(block_size / 10)
        glitch_queue = BoundedGlitchQueue(max_size=save_blocks) if save_blocks else None

        output.log(f"Analyzing file: {filename}")
        output.log(f"Sample rate: {sample_rate} Hz")
        output.log(f"Channels: {channels}")
        output.log(f"Bit depth: {bit_depth}")
        output.log(f"Duration: {duration:.2f} seconds")
        output.log(f"Block size: {block_size} frames")
        output.log(f"Overlap: {overlap} samples")
        output.log(f"Detection threshold: {threshold if threshold > 0 else 'auto'}")

        total_block_count = math.ceil(total_frames / (block_size - overlap))

        with FileReader(filename, block_size=block_size, overlap=overlap) as reader:
            detector = GlitchDetector(reader.sample_rate, threshold)

            all_glitch_indices = []
            all_glitch_timestamps = []

            # Process blocks with progress bar
            with tqdm(total=total_block_count, desc="Processing", unit="block") as pbar:
                for samples, frame_offset in reader.read_blocks():
                    result = detector.detect_with_offset(samples, frame_offset)

                    all_glitch_indices.extend(result.sample_indices)
                    all_glitch_timestamps.extend(result.timestamps_ms)

                    # Store block for later saving if glitches detected
                    if save_blocks and glitch_queue and result.total_count > 0:
                        glitch_queue.add_block(samples, reader.sample_rate, frame_offset, result.threshold)

                    pbar.update(1)

            unique_indices = sorted(set(all_glitch_indices))
            unique_timestamps = [format_time_string(detector._sample_to_milliseconds(idx)) for idx in unique_indices]

            output.print_results(len(unique_indices), unique_timestamps)

            # Process saved blocks if enabled
            if save_blocks and glitch_queue and glitch_queue.count() > 0:
                output.log(
                    f"\nSaving {glitch_queue.count()} glitch blocks...",
                    style="bold yellow",
                )

                with tqdm(total=glitch_queue.count(), desc="Saving blocks", unit="block") as pbar:
                    for block in glitch_queue.get_all_blocks():
                        save_glitch_block(
                            block.samples,
                            block.sample_rate,
                            block.frame_offset,
                            block.threshold,
                        )
                        pbar.update(1)

                current_dir = Path.cwd()
                output.log(
                    f"Saved {glitch_queue.count()} glitch blocks to '{current_dir}/glitch_artifacts/'",
                    style="bold green",
                )

    except Exception as e:
        output.log(f"Error processing file: {e}", style="bold red")
        sys.exit(1)
