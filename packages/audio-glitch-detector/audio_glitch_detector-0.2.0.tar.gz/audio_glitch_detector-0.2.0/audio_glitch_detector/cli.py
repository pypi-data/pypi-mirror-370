import argparse
import sys
from importlib.metadata import version

from .audio import AudioConfig
from .file_mode import run_file_mode
from .stream_mode import run_stream_mode
from .tui import ConsoleOutput


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(description="Detect audio glitches and discontinuities in sinusoidal signals")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"audio-glitch-detector {version('audio-glitch-detector')}",
    )
    parser.add_argument(
        "-f",
        "--filename",
        help="Audio file to analyze",
    )
    parser.add_argument(
        "-r",
        "--sample_rate",
        type=int,
        default=48000,
        help="Sample rate for stream mode (default: 48000)",
    )
    parser.add_argument(
        "-c",
        "--channels",
        type=int,
        default=2,
        choices=[1, 2],
        help="Number of channels for stream mode (default: 2)",
    )
    parser.add_argument(
        "--bit_depth",
        type=int,
        default=32,
        choices=[16, 32],
        help="Bit depth for stream mode (default: 32)",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=1024,
        help="Block size (frames) for processing (default: 1024)",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.0,
        help="discontinuity detection threshold. 0 = auto. (default: auto)",
    )
    parser.add_argument(
        "-s",
        "--save-blocks",
        nargs="?",
        const=50,
        type=int,
        metavar="n",
        help="Save audio blocks containing glitches as .wav files and a visualization. Optional max blocks to save (default: 50)",
    )
    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    output = ConsoleOutput()

    if args.filename:
        run_file_mode(args.filename, args.threshold, args.block_size, args.save_blocks, output)
    else:
        config = AudioConfig(
            sample_rate=args.sample_rate,
            channels=args.channels,
            bit_depth=args.bit_depth,
            block_size=args.block_size,
        )

        try:
            config.validate()
        except ValueError as e:
            output.log(f"Invalid configuration: {e}", style="bold red")
            sys.exit(1)

        run_stream_mode(config, args.threshold, args.save_blocks, output)


if __name__ == "__main__":
    main()
