"""
Streaming mode for QuickDownload.
Downloads files sequentially with auto-playback for media files.
"""

import os
import sys
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import (
    _get_file_info,
    _download_chunk,
    _format_size,
    _save_progress,
    _load_progress,
    _cleanup_orphaned_part_files,
)


def is_media_file(filename):
    """Check if file is a media file that can be streamed."""
    media_extensions = {
        # Video
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".mpg",
        ".mpeg",
        ".3gp",
        ".ogv",
        ".ts",
        ".m2ts",
        ".mts",
        # Audio
        ".mp3",
        ".flac",
        ".wav",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
        ".opus",
        ".ape",
        ".ac3",
        ".dts",
    }

    ext = os.path.splitext(filename.lower())[1]
    return ext in media_extensions


def get_media_bitrate_estimate(filename):
    """Get conservative bitrate estimate based on file extension."""
    ext = os.path.splitext(filename.lower())[1]

    # Conservative estimates in bits per second
    bitrate_estimates = {
        # Video (conservative estimates for smooth streaming)
        ".mp4": 3_000_000,  # 3 Mbps
        ".mkv": 5_000_000,  # 5 Mbps
        ".avi": 2_000_000,  # 2 Mbps
        ".webm": 1_500_000,  # 1.5 Mbps
        ".mov": 4_000_000,  # 4 Mbps
        ".wmv": 2_000_000,  # 2 Mbps
        ".flv": 1_000_000,  # 1 Mbps
        ".m4v": 3_000_000,  # 3 Mbps
        ".mpg": 2_000_000,  # 2 Mbps
        ".mpeg": 2_000_000,  # 2 Mbps
        # Audio
        ".mp3": 320_000,  # 320 kbps
        ".flac": 1_000_000,  # ~1 Mbps
        ".wav": 1_400_000,  # 1.4 Mbps
        ".aac": 256_000,  # 256 kbps
        ".ogg": 320_000,  # 320 kbps
        ".m4a": 256_000,  # 256 kbps
        ".opus": 128_000,  # 128 kbps
        ".wma": 256_000,  # 256 kbps
    }

    return bitrate_estimates.get(ext, 2_000_000)  # 2 Mbps default


def find_media_player():
    """Find available media player."""
    players = [
        (["vlc", "--play-and-exit"], "VLC"),  # Play and exit when done
        (["mpv", "--keep-open=no"], "MPV"),
        (["ffplay", "-autoexit"], "FFplay"),
        (["mplayer"], "MPlayer"),
    ]

    for cmd, name in players:
        if shutil.which(cmd[0]):
            return cmd, name

    return None, None


def _get_playback_threshold(filename, file_size, downloaded_bytes, buffer_bytes):
    """
    Determine the minimum threshold for starting playback based on file type.
    Modern players can handle progressive downloads like HTML5, so start early.
    """
    ext = os.path.splitext(filename.lower())[1]

    # For small files, start immediately when first chunk is ready
    if file_size < 5 * 1024 * 1024:  # Files under 5MB
        return max(buffer_bytes * 0.1, 256 * 1024)  # Minimal threshold

    # For all media files, use HTML5-style progressive loading
    # Start as soon as we have a reasonable buffer (like HTML5 does)
    if ext in [".mp4", ".mkv", ".avi", ".webm", ".mov", ".flv", ".m4v"]:
        # For video: start with 2-5 seconds worth of content
        return max(buffer_bytes * 0.2, 2 * 1024 * 1024)  # Min 2MB or 20% of buffer

    # Audio files can start with even less buffering
    elif ext in [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]:
        return max(buffer_bytes * 0.1, 512 * 1024)  # Min 512KB or 10% of buffer

    # Default for other media types
    else:
        return max(buffer_bytes * 0.3, 1024 * 1024)  # Min 1MB or 30% of buffer


def download_streaming(
    url, output=None, parallel=4, buffer_seconds=30, throttle_limit=None
):
    """
    Download with streaming mode: sequential chunks + auto-play for media files.

    Args:
        url: URL to download
        output: Output filename (auto-detected if None)
        parallel: Number of parallel connections
        buffer_seconds: Seconds of media to buffer before starting playback
        throttle_limit: Bandwidth limit per chunk (e.g., "1M", "500k")
    """

    print("QuickDownload - Streaming Mode")
    print("=" * 50)

    # Parse and validate throttle limit
    throttle_bps = None
    if throttle_limit:
        from .throttle import parse_bandwidth_limit, format_bandwidth

        try:
            throttle_bps = parse_bandwidth_limit(throttle_limit)
            if throttle_bps:
                print(f"Bandwidth limit: {format_bandwidth(throttle_bps)} per chunk")
            else:
                print("Bandwidth limit: unlimited")
        except ValueError as e:
            print(f"Error: {e}")
            return False

    # Get file info
    try:
        print("Analyzing file... ", end="", flush=True)
        file_size, supports_ranges, auto_filename = _get_file_info(url)
        print("✓")
    except Exception as e:
        print(f"Error getting file info: {e}")
        return False

    if output is None:
        output = auto_filename

    print(f"File: {output}")
    print(f"Size: {_format_size(file_size)}")
    print(f"Range requests supported: {supports_ranges}")

    if not supports_ranges:
        print("Server doesn't support range requests.")
        print("Falling back to single-threaded download...")
        from .utils import _download_single_threaded

        return _download_single_threaded(url, output, throttle_bps)

    # Check if it's a media file
    is_media = is_media_file(output)
    player_cmd = None
    player_name = None

    if is_media:
        print("Media file detected - will auto-play when ready")
        print("Using HTML5-style progressive download for immediate playback")
        player_cmd, player_name = find_media_player()

        if player_cmd:
            print(f"Media player: {player_name}")
        else:
            print(
                "No media player found (install vlc, mpv, or ffplay for auto-playback)"
            )
            is_media = False
    else:
        print("Non-media file - using streaming chunk strategy without auto-play")

    # Calculate streaming parameters
    if is_media and player_cmd:
        bitrate_bps = get_media_bitrate_estimate(output)
        bytes_per_second = bitrate_bps // 8
        buffer_bytes = bytes_per_second * buffer_seconds

        print(f"Estimated bitrate: {bitrate_bps/1000:.1f} kbps")
        print(f"Buffer target: {_format_size(buffer_bytes)} ({buffer_seconds}s)")
    else:
        buffer_bytes = 10 * 1024 * 1024  # 10MB default buffer

    # Use smaller chunks for streaming (better granularity)
    if is_media:
        chunk_size = min(
            file_size // (parallel * 4), 2 * 1024 * 1024
        )  # Max 2MB chunks for media
    else:
        chunk_size = min(
            file_size // (parallel * 2), 10 * 1024 * 1024
        )  # Max 10MB chunks for other files

    chunk_size = max(
        chunk_size, min(512 * 1024, file_size)
    )  # Min 512KB chunks, but not larger than file
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    print(f"Chunk strategy: {total_chunks} chunks of ~{_format_size(chunk_size)} each")
    print()

    # Create throttle instances for streaming (if throttling enabled)
    throttles = []
    if throttle_bps:
        from .throttle import BandwidthThrottle, format_bandwidth

        for _ in range(parallel):
            throttles.append(BandwidthThrottle(throttle_bps))
        total_limit = format_bandwidth(throttle_bps * parallel)
        print(
            f"Total bandwidth limit: {total_limit} ({parallel} chunks × {format_bandwidth(throttle_bps)})"
        )
        print()
    else:
        throttles = [None] * parallel

    # Clean up any existing chunk files
    _cleanup_orphaned_part_files(output, total_chunks)  # Check for existing progress
    existing_progress = _load_progress(output)
    completed_chunks = set()

    if existing_progress and existing_progress.get("url") == url:
        completed_chunks = set(existing_progress.get("completed_chunks", []))
        if completed_chunks:
            print(
                f"Resuming download: {len(completed_chunks)}/{total_chunks} chunks completed"
            )

    # Create a properly sized file for progressive writing (like HTML5)
    if is_media and player_cmd:
        try:
            # Create file with correct size and fill with zeros (sparse-like but compatible)
            with open(output, "wb") as f:
                f.seek(file_size - 1)
                f.write(b"\0")
            print(f"Created properly sized file for streaming: {output}")
        except Exception as e:
            print(f"Warning: Could not create file: {e}")

    # Download with streaming priority
    player_started = False
    player_process = None
    downloaded_bytes = len(completed_chunks) * chunk_size

    print("Starting streaming download...")
    print()

    try:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            # Submit chunks in sequential order for streaming
            future_to_chunk = {}

            # Submit first batch (prioritize early chunks)
            batch_size = parallel * 2
            for chunk_id in range(min(batch_size, total_chunks)):
                if chunk_id not in completed_chunks:
                    future = executor.submit(
                        _download_streaming_chunk,
                        url,
                        chunk_id,
                        chunk_size,
                        file_size,
                        output,
                        throttles[
                            chunk_id % parallel
                        ],  # Distribute throttles among chunks
                    )
                    future_to_chunk[future] = chunk_id

            # Process completions
            next_chunk_to_submit = batch_size

            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]

                try:
                    success = future.result()
                    if success:
                        completed_chunks.add(chunk_id)
                        downloaded_bytes = len(completed_chunks) * chunk_size

                        # IMMEDIATELY write chunk to main file for real-time streaming
                        _assemble_chunk_to_file(output, chunk_id, chunk_size, file_size)

                        # Update progress file
                        _save_progress(
                            output, url, file_size, total_chunks, list(completed_chunks)
                        )

                        # Start player when we have enough buffer OR for small files
                        # For MP4 files, wait for more content since MOOV atom is usually at the end
                        min_threshold = _get_playback_threshold(
                            output, file_size, downloaded_bytes, buffer_bytes
                        )

                        if (
                            is_media
                            and player_cmd
                            and not player_started
                            and downloaded_bytes >= min_threshold
                            and 0 in completed_chunks
                        ):  # Must have first chunk

                            print(f"\nBuffer ready! Starting {player_name}...")
                            try:
                                # Assemble file from completed chunks first
                                _assemble_completed_chunks(
                                    output, completed_chunks, chunk_size, file_size
                                )

                                # Give VLC a moment to recognize the file content
                                import time

                                time.sleep(0.5)

                                player_process = subprocess.Popen(
                                    player_cmd + [output],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                )
                                player_started = True
                                print(f"{player_name} started successfully!")
                                print(
                                    "Video should start playing as content becomes available..."
                                )
                                print()

                            except Exception as e:
                                print(f"Failed to start {player_name}: {e}")
                                print(
                                    "You can manually play the file once download completes."
                                )

                    else:
                        print(f"Failed to download chunk {chunk_id}")

                except Exception as e:
                    print(f"Error downloading chunk {chunk_id}: {e}")

                # Submit next chunk to keep pipeline full
                if next_chunk_to_submit < total_chunks:
                    if next_chunk_to_submit not in completed_chunks:
                        future = executor.submit(
                            _download_streaming_chunk,
                            url,
                            next_chunk_to_submit,
                            chunk_size,
                            file_size,
                            output,
                            throttles[
                                next_chunk_to_submit % parallel
                            ],  # Distribute throttles
                        )
                        future_to_chunk[future] = next_chunk_to_submit
                    next_chunk_to_submit += 1

                # Show progress
                progress = (len(completed_chunks) / total_chunks) * 100
                _show_streaming_progress(
                    progress,
                    downloaded_bytes,
                    file_size,
                    len(completed_chunks),
                    total_chunks,
                )

                # Check if download complete
                if len(completed_chunks) == total_chunks:
                    break

    except KeyboardInterrupt:
        print("\nDownload interrupted. Progress saved.")
        if player_process:
            player_process.terminate()
        return False

    # Final assembly
    print("\nDownload complete! Assembling final file...")
    _assemble_final_file(output, total_chunks, chunk_size, file_size)

    # Clean up chunk files
    for chunk_id in range(total_chunks):
        chunk_file = f"{output}.part{chunk_id}"
        if os.path.exists(chunk_file):
            os.remove(chunk_file)

    # Clean up progress file
    progress_file = f"{output}.progress"
    if os.path.exists(progress_file):
        os.remove(progress_file)

    print(f"File saved: {output}")

    if player_started:
        print(f"{player_name} should continue playing the complete file.")

    return True


def _download_streaming_chunk(
    url, chunk_id, chunk_size, file_size, output, throttle=None
):
    """Download a single chunk for streaming."""
    start_byte = chunk_id * chunk_size
    end_byte = min(start_byte + chunk_size - 1, file_size - 1)
    chunk_file = f"{output}.part{chunk_id}"

    try:
        # Use the existing _download_chunk function with retry logic and throttling
        bytes_downloaded = _download_chunk(
            url, start_byte, end_byte, chunk_file, chunk_id, throttle
        )
        return bytes_downloaded is not None and bytes_downloaded > 0
    except Exception:
        return False


def _assemble_chunk_to_file(output, chunk_id, chunk_size, file_size):
    """Immediately assemble a completed chunk into the main file."""
    chunk_file = f"{output}.part{chunk_id}"

    if not os.path.exists(chunk_file):
        return

    try:
        with open(output, "r+b") as main_file:
            main_file.seek(chunk_id * chunk_size)

            with open(chunk_file, "rb") as cf:
                while True:
                    data = cf.read(8192)
                    if not data:
                        break
                    main_file.write(data)

    except Exception as e:
        print(f"Warning: Could not assemble chunk {chunk_id}: {e}")


def _assemble_completed_chunks(output, completed_chunks, chunk_size, file_size):
    """Assemble all completed chunks into the main file."""
    for chunk_id in sorted(completed_chunks):
        _assemble_chunk_to_file(output, chunk_id, chunk_size, file_size)


def _assemble_final_file(output, total_chunks, chunk_size, file_size):
    """Assemble the final complete file from all chunks."""
    try:
        with open(output, "wb") as main_file:
            for chunk_id in range(total_chunks):
                chunk_file = f"{output}.part{chunk_id}"

                if os.path.exists(chunk_file):
                    with open(chunk_file, "rb") as cf:
                        while True:
                            data = cf.read(8192)
                            if not data:
                                break
                            main_file.write(data)

    except Exception as e:
        print(f"Error assembling final file: {e}")
        raise


def _show_streaming_progress(
    progress, downloaded, total, completed_chunks, total_chunks
):
    """Show streaming download progress."""

    # Progress bar
    bar_width = 40
    filled = int(bar_width * progress / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    # Format sizes
    downloaded_str = _format_size(downloaded)
    total_str = _format_size(total)

    progress_text = (
        f"\r[{bar}] {progress:.1f}% "
        f"({downloaded_str}/{total_str}) "
        f"Chunks: {completed_chunks}/{total_chunks}   "
    )

    sys.stdout.write(progress_text)
    sys.stdout.flush()
