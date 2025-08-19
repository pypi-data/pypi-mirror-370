from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class GlitchBlock:
    """Container for a glitch block with metadata."""

    samples: np.ndarray
    sample_rate: int
    frame_offset: int
    threshold: float
    timestamp_ms: float


class BoundedGlitchQueue:
    """A bounded queue that stores the most recent glitch blocks."""

    def __init__(self, max_size: int = 50):
        """Initialize with maximum number of blocks to store."""
        self.max_size = max_size
        self._queue = deque(maxlen=max_size)

    def add_block(self, samples: np.ndarray, sample_rate: int, frame_offset: int, threshold: float) -> None:
        """Add a glitch block to the queue. Oldest blocks are automatically dropped if full."""
        timestamp_ms = (frame_offset / sample_rate) * 1000
        block = GlitchBlock(
            samples=samples.copy(),
            sample_rate=sample_rate,
            frame_offset=frame_offset,
            threshold=threshold,
            timestamp_ms=timestamp_ms,
        )
        self._queue.append(block)

    def get_all_blocks(self) -> Iterator[GlitchBlock]:
        """Get all stored glitch blocks."""
        return iter(self._queue)

    def count(self) -> int:
        """Get the number of stored blocks."""
        return len(self._queue)

    def clear(self) -> None:
        """Clear all stored blocks."""
        self._queue.clear()
