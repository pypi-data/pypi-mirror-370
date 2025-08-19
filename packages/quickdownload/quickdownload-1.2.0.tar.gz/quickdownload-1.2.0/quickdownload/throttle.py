"""
Bandwidth throttling utilities for QuickDownload.
Provides per-chunk speed limiting with precise rate control.
"""

import time
import re
from typing import Optional


class BandwidthThrottle:
    """
    Bandwidth throttling manager for controlling download speeds.
    Implements token bucket algorithm for smooth rate limiting.
    """

    def __init__(self, max_bytes_per_second: Optional[int] = None):
        """
        Initialize throttle with maximum bytes per second.

        Args:
            max_bytes_per_second: Maximum bytes allowed per second (None = unlimited)
        """
        self.max_bytes_per_second = max_bytes_per_second
        self.last_update = time.time()
        self.tokens = 0.0  # Available bytes to download
        self.bucket_size = (
            max_bytes_per_second * 2 if max_bytes_per_second else 0
        )  # 2 second burst

    def throttle(self, bytes_downloaded: int):
        """
        Apply throttling delay based on bytes downloaded.

        Args:
            bytes_downloaded: Number of bytes just downloaded
        """
        if not self.max_bytes_per_second:
            return  # No throttling

        current_time = time.time()
        time_elapsed = current_time - self.last_update

        # Add tokens based on elapsed time
        self.tokens += time_elapsed * self.max_bytes_per_second
        self.tokens = min(self.tokens, self.bucket_size)  # Cap at bucket size

        # Consume tokens for downloaded bytes
        self.tokens -= bytes_downloaded

        # If we're out of tokens, sleep until we have enough
        if self.tokens < 0:
            sleep_time = abs(self.tokens) / self.max_bytes_per_second
            time.sleep(sleep_time)
            self.tokens = 0

        self.last_update = current_time


def parse_bandwidth_limit(limit_str: str) -> Optional[int]:
    """
    Parse bandwidth limit string into bytes per second.

    Args:
        limit_str: Bandwidth limit string (e.g., "1M", "500k", "30K", "1.5MB")

    Returns:
        Bytes per second as integer, or None if unlimited

    Examples:
        "1M" or "1m" -> 1,000,000 bytes/sec (1 Mbps)
        "1MB" -> 1,000,000 bytes/sec
        "30k" or "30K" -> 30,000 bytes/sec (30 Kbps)
        "30KB" -> 30,000 bytes/sec
        "1.5M" -> 1,500,000 bytes/sec
        "500" -> 500 bytes/sec
        "unlimited" -> None
    """

    if not limit_str or limit_str.lower() in ["unlimited", "none", "0"]:
        return None

    # Remove whitespace and convert to lowercase for processing
    limit_str = limit_str.strip().lower()

    # Regular expression to parse number and unit
    pattern = r"^(\d+(?:\.\d+)?)\s*([kmgt]?b?)?$"
    match = re.match(pattern, limit_str)

    if not match:
        raise ValueError(f"Invalid bandwidth limit format: {limit_str}")

    number_str, unit = match.groups()
    number = float(number_str)

    # Parse unit (default to bytes if no unit specified)
    unit = unit or "b"

    # Define multipliers (using decimal, not binary)
    # Network speeds are typically measured in decimal (1 Mbps = 1,000,000 bps)
    multipliers = {
        "b": 1,  # bytes
        "k": 1_000,  # kilobytes (1 KB = 1,000 bytes)
        "kb": 1_000,  # kilobytes
        "m": 1_000_000,  # megabytes (1 MB = 1,000,000 bytes)
        "mb": 1_000_000,  # megabytes
        "g": 1_000_000_000,  # gigabytes
        "gb": 1_000_000_000,  # gigabytes
        "t": 1_000_000_000_000,  # terabytes
        "tb": 1_000_000_000_000,  # terabytes
    }

    if unit not in multipliers:
        raise ValueError(f"Unknown unit: {unit}")

    bytes_per_second = int(number * multipliers[unit])

    # Sanity checks
    if bytes_per_second < 1:
        raise ValueError("Bandwidth limit must be at least 1 byte/second")
    if bytes_per_second > 10_000_000_000:  # 10 GB/s seems reasonable max
        raise ValueError("Bandwidth limit too high")

    return bytes_per_second


def format_bandwidth(bytes_per_second: Optional[int]) -> str:
    """
    Format bytes per second into human-readable string.

    Args:
        bytes_per_second: Bytes per second

    Returns:
        Formatted string (e.g., "1.5 Mbps", "30 Kbps")
    """
    if bytes_per_second is None:
        return "unlimited"

    if bytes_per_second >= 1_000_000:
        return f"{bytes_per_second / 1_000_000:.1f} Mbps"
    elif bytes_per_second >= 1_000:
        return f"{bytes_per_second / 1_000:.1f} Kbps"
    else:
        return f"{bytes_per_second} bps"


# Test the parsing function
if __name__ == "__main__":
    test_cases = [
        "1M",
        "1m",
        "1MB",
        "1mb",
        "30k",
        "30K",
        "30KB",
        "30kb",
        "1.5M",
        "500k",
        "100",
        "2.5MB",
        "10G",
        "unlimited",
    ]

    for case in test_cases:
        try:
            result = parse_bandwidth_limit(case)
            formatted = format_bandwidth(result)
            print(f"{case:10} -> {result:>12} bytes/sec -> {formatted}")
        except Exception as e:
            print(f"{case:10} -> ERROR: {e}")
