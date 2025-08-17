import signal
import sys
from threading import Event

from tqdm import tqdm

from .audio import (
    AudioConfig,
    BoundedGlitchQueue,
    save_glitch_block,
    print_audio_devices,
)
from .readers import StreamReader
from .core import GlitchDetector
from .tui import ConsoleOutput


def select_audio_device(output: ConsoleOutput) -> int | None:
    """Get audio device ID from user input."""
    output.console.print("\nSelect audio device")
    print_audio_devices()

    try:
        device_input = input("Device ID: ")
        return int(device_input)
    except (ValueError, KeyboardInterrupt):
        output.log("Invalid device ID or cancelled", style="bold red")
        return None


def process_saved_blocks(glitch_queue: BoundedGlitchQueue | None, output: ConsoleOutput) -> None:
    """Process and save queued glitch blocks."""
    if not (glitch_queue and glitch_queue.count() > 0):
        return

    output.log(f"\nSaving {glitch_queue.count()} glitch blocks...", style="bold yellow")

    with tqdm(total=glitch_queue.count(), desc="Saving blocks", unit="block") as pbar:
        for block in glitch_queue.get_all_blocks():
            save_glitch_block(block.samples, block.sample_rate, block.frame_offset, block.threshold)
            pbar.update(1)

    output.log(
        f"Saved {glitch_queue.count()} glitch blocks to 'glitch_artifacts/' folder",
        style="bold green",
    )


def run_stream_mode(config: AudioConfig, threshold: float, save_blocks: bool, output: ConsoleOutput) -> None:
    """Run real-time glitch detection on an audio stream."""
    exit_event = Event()
    glitch_queue = BoundedGlitchQueue(max_size=50) if save_blocks else None
    glitch_count = 0

    # Setup signal handler
    signal.signal(signal.SIGINT, lambda sig, frame: exit_event.set())

    device_id = select_audio_device(output)
    if device_id is None:
        return

    def glitch_callback(samples, frame_number):
        nonlocal glitch_count
        detector = GlitchDetector(config.sample_rate, threshold)
        result = detector.detect_with_offset(samples, frame_number)

        if result.total_count > 0:
            glitch_count += result.total_count
            if result.auto_threshold:
                auto_threshold_str = f" (threshold: {result.threshold:.2f})"
            else:
                auto_threshold_str = ""

            output.log(
                f"Glitch detected!{auto_threshold_str} Total: {glitch_count}",
                style="bold red",
            )

            if save_blocks and glitch_queue:
                glitch_queue.add_block(samples, config.sample_rate, frame_number, threshold)

    try:
        with StreamReader(config, device_id) as stream:
            output.print_header("Audio Glitch Detector Live")
            output.reset_timer()
            output.log(f"Analyzing audio stream from device id: {device_id}")
            output.log(f"Sample rate: {config.sample_rate} Hz")
            output.log(f"Channels: {config.channels}")
            output.log(f"Block size: {config.block_size} frames")
            output.log(f"Detection threshold: {threshold if threshold > 0 else 'auto'}")

            # Start monitoring
            thread = stream.start_monitoring(glitch_callback, exit_event)
            output.start_live_output(exit_event, lambda: stream.get_volume_db())

            # Wait for completion
            thread.join()

            # Cleanup and summary
            output.stop_live_output()
            output.print_summary(glitch_count, output.get_elapsed_time())

            # Process saved blocks
            process_saved_blocks(glitch_queue, output)

    except Exception as e:
        output.log(f"Stream error: {e}", style="bold red")
        sys.exit(1)
