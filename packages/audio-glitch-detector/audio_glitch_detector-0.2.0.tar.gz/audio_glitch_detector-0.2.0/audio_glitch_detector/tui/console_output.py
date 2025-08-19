import time
from collections.abc import Callable
from threading import Event, Lock, Thread

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..utils.time_utils import format_elapsed_time


class ConsoleOutput:
    """Rich console output for the CLI interface."""

    def __init__(self):
        self.console = Console()
        self.start_time = time.time()
        self.lock = Lock()
        self.running = False
        self.elapsed_time = "00:00:00"
        self.volume_levels = [0.0, 0.0]

    def print_header(self, title: str) -> None:
        """Print a formatted header."""
        header = Panel(Text(title, justify="center"), style="bold white")
        self.console.print(header)

    def log(self, message: str, style: str = "") -> None:
        """Print a log message with timestamp."""
        with self.lock:
            self.console.log(message, style=style)

    def print_banner(self) -> None:
        """Print a separator banner."""
        self.console.print("-" * 71)

    def reset_timer(self) -> None:
        """Reset the elapsed time timer."""
        self.start_time = time.time()

    def start_live_output(
        self,
        exit_event: Event,
        volume_callback: Callable[[], list[float]],
    ) -> None:
        """Start live output display in background thread."""
        self.running = True
        thread = Thread(target=self._live_output_loop, args=(exit_event, volume_callback))
        thread.start()

    def stop_live_output(self) -> None:
        """Stop the live output display."""
        self.running = False

    def _calculate_elapsed_time(self) -> str:
        """Calculate elapsed time since start."""
        elapsed_seconds = time.time() - self.start_time
        self.elapsed_time = format_elapsed_time(elapsed_seconds)
        return self.elapsed_time

    def get_elapsed_time(self) -> str:
        """Get the current elapsed time."""
        return self.elapsed_time

    def _create_live_panel(self) -> Panel:
        """Create the live output panel."""
        table = Table.grid(expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right", ratio=1)

        volume_text = f"{self.volume_levels[0]:.1f}dB\n{self.volume_levels[1]:.1f}dB"
        time_text = self.get_elapsed_time()

        table.add_row(volume_text, time_text)
        table.add_row("", "")  # Empty row for spacing
        table.add_row(Text("ctrl-c to quit", style="dim"), "")

        return Panel(table, title="Volume", style="bold white")

    def _live_output_loop(self, exit_event: Event, volume_callback: Callable[[], list[float]]) -> None:
        """Main loop for live output display."""
        with Live(self._create_live_panel(), console=self.console, auto_refresh=False) as live:
            while self.running and not exit_event.is_set():
                self._calculate_elapsed_time()
                self.volume_levels = volume_callback()
                live.update(self._create_live_panel())
                live.refresh()
                time.sleep(0.1)

    def print_results(self, glitch_count: int, timestamps: list[str]) -> None:
        """Print detection results."""
        self.print_banner()
        self.console.print(f"Number of discontinuities detected: {glitch_count}")

        for timestamp in timestamps:
            self.console.print(timestamp)

        self.print_banner()

    def print_summary(self, total_count: int, elapsed_time: str) -> None:
        """Print final summary."""
        self.log(
            f"Total discontinuities detected: {total_count} in {elapsed_time}",
            style="bold red",
        )
