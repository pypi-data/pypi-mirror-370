from datetime import timedelta


def time_to_milliseconds(frame_number: int, sample_rate: int) -> float:
    """Convert frame number to milliseconds."""
    return (frame_number / sample_rate) * 1000.0


def format_time(milliseconds: float) -> timedelta:
    """Convert milliseconds to a formatted timedelta object."""
    return timedelta(milliseconds=milliseconds)


def format_time_string(milliseconds: float) -> str:
    """Format milliseconds as HH:MM:SS.mmm string."""
    td = format_time(milliseconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ms = td.microseconds // 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def format_elapsed_time(seconds: float) -> str:
    """Format elapsed time in seconds as HH:MM:SS."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
