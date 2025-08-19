import os
import sys
import time
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from . import __version__

# Global progress tracking for multi-chunk downloads
chunk_progress = {}
progress_lock = threading.Lock()


def get_user_agent_fallbacks(is_media=False):
    """
    Get progressive User-Agent fallback list.

    Args:
        is_media: If True, include VLC agent for media files

    Returns:
        List of (user_agent, description) tuples to try in order
    """

    # Standard fallback progression
    fallbacks = [
        (None, "Python default"),  # Let urllib use default
        (f"QuickDownload/{__version__}", "QuickDownload"),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Chrome browser",
        ),
    ]

    # Add VLC agent for media files
    if is_media:
        fallbacks.append(("VLC/3.0.18 LibVLC/3.0.18", "VLC media player"))

    return fallbacks


def _make_request_with_fallback(
    url, method="HEAD", range_header=None, is_media=False, timeout=30
):
    """
    Make HTTP request with progressive User-Agent fallback.

    Args:
        url: URL to request
        method: HTTP method (HEAD or GET)
        range_header: Range header value if needed
        is_media: Whether this is for a media file
        timeout: Request timeout

    Returns:
        urllib response object

    Raises:
        Exception: If all fallbacks fail
    """

    fallbacks = get_user_agent_fallbacks(is_media)
    last_error = None

    for i, (user_agent, description) in enumerate(fallbacks):
        try:
            if i > 0:  # Show fallback attempt (but not for first default attempt)
                print(f"  → Trying {description}...", end="", flush=True)

            # Create request
            req = urllib.request.Request(url, method=method)

            # Add User-Agent if specified
            if user_agent:
                req.add_header("User-Agent", user_agent)

            # Add Range header if specified
            if range_header:
                req.add_header("Range", range_header)

            # Make request
            response = urllib.request.urlopen(req, timeout=timeout)

            if i > 0:  # Show success for fallback attempts
                print(" ✓")

            return response

        except (HTTPError, URLError) as e:
            last_error = e

            if i > 0:  # Show failure for fallback attempts
                if isinstance(e, HTTPError):
                    print(f" ✗ (HTTP {e.code})")
                else:
                    print(f" ✗ ({str(e)})")

            # For 403/401 errors, continue trying other agents
            if isinstance(e, HTTPError) and e.code in [403, 401, 429]:
                continue

            # For other HTTP errors, maybe the file doesn't exist
            if isinstance(e, HTTPError) and e.code in [404, 410]:
                break

            # For connection errors, continue trying
            continue

        except Exception as e:
            last_error = e
            if i > 0:
                print(f" ✗ ({str(e)})")
            continue

    # All fallbacks failed
    if isinstance(last_error, HTTPError):
        raise Exception(f"Failed to get file info: HTTP {last_error.code}")
    else:
        raise Exception(f"Failed to get file info: {str(last_error)}")


def _get_progress_file(output):
    """Get the progress tracking file path."""
    return f"{output}.progress"


def _save_progress(output, url, file_size, parallel, completed_chunks):
    """Save download progress to a file."""
    progress_data = {
        "url": url,
        "output": output,
        "file_size": file_size,
        "parallel": parallel,
        "completed_chunks": completed_chunks,
        "timestamp": time.time(),
    }
    progress_file = _get_progress_file(output)
    try:
        with open(progress_file, "w") as f:
            json.dump(progress_data, f)
    except Exception:
        pass  # Continue even if we can't save progress


def _load_progress(output):
    """Load download progress from a file."""
    progress_file = _get_progress_file(output)
    try:
        if os.path.exists(progress_file):
            with open(progress_file, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def _remap_chunks_for_different_parallelism(
    existing_progress, new_parallel, file_size, output
):
    """
    Smart chunk remapping that preserves existing progress when parallelism changes.
    This function handles both consolidation (e.g., 9→4 parts) and splitting (e.g., 4→9 parts).
    Returns a set of new chunk IDs that are fully covered by existing completed chunks.
    """
    old_parallel = existing_progress.get("parallel", 1)
    old_completed = set(existing_progress.get("completed_chunks", []))

    if not old_completed:
        return set()

    print(f"Smart remapping: {old_parallel} → {new_parallel} parts...")

    # Calculate chunk sizes
    old_chunk_size = file_size // old_parallel
    new_chunk_size = file_size // new_parallel

    print(f"  Old chunk size: {_format_size(old_chunk_size)}")
    print(f"  New chunk size: {_format_size(new_chunk_size)}")

    # Build a map of what data we have available from completed old chunks
    available_data_ranges = []
    old_temp_files = {}

    for old_chunk_id in sorted(old_completed):
        if old_chunk_id < old_parallel:
            start = old_chunk_id * old_chunk_size
            end = start + old_chunk_size - 1
            if old_chunk_id == old_parallel - 1:  # Last chunk gets remainder
                end = file_size - 1

            old_temp_file = f"{output}.part{old_chunk_id}"
            if os.path.exists(old_temp_file):
                # Verify the chunk file is correct size
                expected_size = end - start + 1
                actual_size = os.path.getsize(old_temp_file)
                if actual_size == expected_size:
                    available_data_ranges.append((start, end))
                    old_temp_files[old_chunk_id] = old_temp_file
                else:
                    print(
                        f"Warning: Old chunk {old_chunk_id} has incorrect size, skipping"
                    )

    if not available_data_ranges:
        print("No valid old chunk data found")
        _cleanup_all_old_part_files(output, old_parallel)
        return set()

    print(f"  Available data ranges: {len(available_data_ranges)} chunks")
    for i, (start, end) in enumerate(available_data_ranges):
        print(f"    Range {i}: bytes {start}-{end} ({_format_size(end-start+1)})")

    # Determine which new chunks can be fully reconstructed
    new_completed = set()
    reconstructed_data = {}  # new_chunk_id -> [(old_file, offset, length)]

    for new_chunk_id in range(new_parallel):
        new_start = new_chunk_id * new_chunk_size
        new_end = new_start + new_chunk_size - 1
        if new_chunk_id == new_parallel - 1:  # Last chunk gets remainder
            new_end = file_size - 1

        print(
            f"  Analyzing new chunk {new_chunk_id}: bytes {new_start}-{new_end} ({_format_size(new_end-new_start+1)})"
        )

        # Check if this new chunk range can be fully covered by available data
        chunk_data_sources = []
        current_pos = new_start

        while current_pos <= new_end:
            # Find which old chunk contains this position
            found_coverage = False

            # Sort available ranges to process them in order
            for range_start, range_end in sorted(available_data_ranges):
                if range_start <= current_pos <= range_end:
                    # Calculate how much data we can get from this range
                    copy_start = current_pos
                    copy_end = min(new_end, range_end)
                    copy_length = copy_end - copy_start + 1

                    # Find which old chunk file contains this data
                    for old_chunk_id, old_file in old_temp_files.items():
                        old_start = old_chunk_id * old_chunk_size
                        old_end_calc = old_start + old_chunk_size - 1
                        if old_chunk_id == old_parallel - 1:
                            old_end_calc = file_size - 1

                        if old_start <= copy_start <= old_end_calc:
                            offset_in_old_file = copy_start - old_start
                            chunk_data_sources.append(
                                (old_file, offset_in_old_file, copy_length)
                            )
                            current_pos = copy_end + 1
                            found_coverage = True
                            break

                    if found_coverage:
                        break  # Found coverage for this position, move to next

            if not found_coverage:
                # This new chunk cannot be fully reconstructed
                print(
                    f"  New chunk {new_chunk_id}: Cannot cover byte range {current_pos}-{new_end}"
                )
                chunk_data_sources = []
                break

        # If we can fully reconstruct this new chunk, add it to completed set
        if chunk_data_sources and current_pos > new_end:
            new_completed.add(new_chunk_id)
            reconstructed_data[new_chunk_id] = chunk_data_sources

    # Report mapping results
    old_completed_count = len(old_completed)
    new_completed_count = len(new_completed)
    old_percentage = (old_completed_count / old_parallel) * 100
    new_percentage = (new_completed_count / new_parallel) * 100

    print("Mapping results:")
    print(
        f"  Old progress: {old_completed_count}/{old_parallel} chunks ({old_percentage:.1f}%)"
    )
    print(
        f"  New progress: {new_completed_count}/{new_parallel} chunks ({new_percentage:.1f}%)"
    )

    if new_completed:
        print(f"Reconstructing {len(new_completed)} new chunks from old data...")

        # First, rename all old chunk files to .old to prevent overwriting
        # This must be done BEFORE any reconstruction starts
        old_files_renamed = {}
        for old_chunk_id, old_file_path in old_temp_files.items():
            old_backup_path = f"{old_file_path}.old"
            try:
                os.rename(old_file_path, old_backup_path)
                old_files_renamed[old_file_path] = old_backup_path
                print(f"  Renamed {old_file_path} → {old_backup_path}")
            except OSError as e:
                print(f"  Warning: Could not rename {old_file_path}: {e}")
                # If we can't rename, use original path (risky but might work)
                old_files_renamed[old_file_path] = old_file_path

        # Update data_sources to use the renamed file paths
        for new_chunk_id in new_completed:
            if new_chunk_id in reconstructed_data:
                updated_sources = []
                for old_file, offset, length in reconstructed_data[new_chunk_id]:
                    renamed_file = old_files_renamed.get(old_file, old_file)
                    updated_sources.append((renamed_file, offset, length))
                reconstructed_data[new_chunk_id] = updated_sources

        # Reconstruct new chunk files
        for new_chunk_id in new_completed:
            new_temp_file = f"{output}.part{new_chunk_id}"
            data_sources = reconstructed_data[new_chunk_id]

            try:
                with open(new_temp_file, "wb") as new_file:
                    for old_file, offset, length in data_sources:
                        with open(old_file, "rb") as old_file_handle:
                            old_file_handle.seek(offset)
                            remaining = length
                            while remaining > 0:
                                chunk = old_file_handle.read(min(8192, remaining))
                                if not chunk:
                                    break
                                new_file.write(chunk)
                                remaining -= len(chunk)

                # Verify the reconstructed chunk
                new_start = new_chunk_id * new_chunk_size
                new_end = new_start + new_chunk_size - 1
                if new_chunk_id == new_parallel - 1:
                    new_end = file_size - 1
                expected_size = new_end - new_start + 1

                if not _verify_chunk(new_temp_file, expected_size):
                    print(
                        f"Warning: Reconstructed chunk {new_chunk_id} failed verification"
                    )
                    new_completed.discard(new_chunk_id)
                    try:
                        os.remove(new_temp_file)
                    except OSError:
                        pass

            except Exception as e:
                print(f"Warning: Failed to reconstruct chunk {new_chunk_id}: {e}")
                new_completed.discard(new_chunk_id)
                try:
                    os.remove(new_temp_file)
                except OSError:
                    pass

    # Clean up ALL old chunk files (regardless of whether they were used)
    _cleanup_all_old_part_files(output, old_parallel)

    # Also clean up any orphaned part files beyond current parallelism
    # This handles cases where previous downloads used higher parallelism
    _cleanup_orphaned_part_files(output, new_parallel)

    print(f"Successfully preserved {len(new_completed)}/{new_parallel} chunks")
    return new_completed


def _cleanup_all_old_part_files(output, old_parallel):
    """Clean up ALL old chunk files from previous download attempt."""
    print(f"Cleaning up old part files (part0 to part{old_parallel-1})...")
    cleaned_count = 0

    for old_chunk_id in range(old_parallel):
        # Clean up both .part and .part.old files
        for suffix in ["", ".old"]:
            old_temp_file = f"{output}.part{old_chunk_id}{suffix}"
            if os.path.exists(old_temp_file):
                try:
                    os.remove(old_temp_file)
                    cleaned_count += 1
                except OSError as e:
                    print(f"Warning: Could not remove {old_temp_file}: {e}")

    if cleaned_count > 0:
        print(f"Removed {cleaned_count} old part files")


def _cleanup_orphaned_part_files(output, current_parallel):
    """Clean up any orphaned part files beyond current parallelism count."""
    print(f"Checking for orphaned part files beyond part{current_parallel-1}...")
    cleaned_count = 0

    # Check for orphaned files up to a reasonable limit (e.g., 100)
    # This covers cases where someone used very high parallelism previously
    for chunk_id in range(current_parallel, 100):
        # Check both .part and .part.old files
        for suffix in ["", ".old"]:
            orphaned_file = f"{output}.part{chunk_id}{suffix}"
            if os.path.exists(orphaned_file):
                try:
                    os.remove(orphaned_file)
                    cleaned_count += 1
                    print(f"  Removed orphaned file: {orphaned_file}")
                except OSError as e:
                    print(f"  Warning: Could not remove {orphaned_file}: {e}")

        # Check if we should continue (optimization for consecutive missing files)
        if not os.path.exists(f"{output}.part{chunk_id}") and not os.path.exists(
            f"{output}.part{chunk_id}.old"
        ):
            # If we find 5 consecutive non-existent files, assume we're done
            # This optimizes the search without checking all 100 files
            consecutive_missing = 0
            for check_id in range(chunk_id, min(chunk_id + 5, 100)):
                if not os.path.exists(
                    f"{output}.part{check_id}"
                ) and not os.path.exists(f"{output}.part{check_id}.old"):
                    consecutive_missing += 1
                else:
                    break

            if consecutive_missing >= 5:
                break

    if cleaned_count > 0:
        print(f"Removed {cleaned_count} orphaned part files")


def _extract_chunk_from_file(source_file, dest_file, offset, size):
    """Extract a portion of data from source file to destination file."""
    try:
        with open(source_file, "rb") as src, open(dest_file, "wb") as dst:
            src.seek(offset)
            remaining = size
            while remaining > 0:
                chunk = src.read(min(8192, remaining))
                if not chunk:
                    break
                dst.write(chunk)
                remaining -= len(chunk)
    except Exception as e:
        raise Exception(f"Failed to extract chunk: {e}")


def _cleanup_old_chunk_files(output, old_parallel, old_completed):
    """Clean up old chunk files that are no longer needed."""
    for old_chunk_id in range(old_parallel):
        old_temp_file = f"{output}.part{old_chunk_id}"
        if os.path.exists(old_temp_file):
            try:
                os.remove(old_temp_file)
            except OSError:
                pass  # Ignore cleanup errors


def _cleanup_progress(output):
    """Remove progress tracking file."""
    progress_file = _get_progress_file(output)
    try:
        if os.path.exists(progress_file):
            os.remove(progress_file)
    except OSError:
        pass


def _verify_chunk(temp_file, expected_size):
    """Verify if a chunk file is complete and valid."""
    try:
        if os.path.exists(temp_file):
            actual_size = os.path.getsize(temp_file)
            return actual_size == expected_size
    except OSError:
        pass
    return False


def download_file(url, output=None, parallel=4, throttle_limit=None):
    """
    Downloads a file from the specified URL with optional output file name and parallel downloads.
    Supports resuming interrupted downloads and bandwidth throttling.
    Args:
        url (str): The URL of the file to download.
        output (str, optional): The output file name. If None, the file will be saved with its original name.
        parallel (int, optional): Number of parallel downloads. Default is 4.
        throttle_limit (str, optional): Bandwidth limit per chunk (e.g., "1M", "500k"). Default is None (unlimited).
        Returns: None
    Raises:
        Exception: If the download fails or if there are issues with the URL.

    """
    try:
        print(f"Starting download from: {url}")

        # Parse and validate throttle limit
        throttle_bps = None
        if throttle_limit:
            from .throttle import parse_bandwidth_limit, format_bandwidth

            try:
                throttle_bps = parse_bandwidth_limit(throttle_limit)
                if throttle_bps:
                    print(
                        f"Bandwidth limit: {format_bandwidth(throttle_bps)} per chunk"
                    )
                else:
                    print("Bandwidth limit: unlimited")
            except ValueError as e:
                print(f"Error: {e}")
                return

        print("Analyzing file... ", end="", flush=True)

        # Get file info and check if range requests are supported
        file_size, supports_ranges, filename = _get_file_info(url)
        print("✓")

        # Determine output filename
        if output is None:
            output = filename

        print(f"File size: {_format_size(file_size)}")
        print(f"Output file: {output}")
        print(f"Range requests supported: {supports_ranges}")

        # Check for existing progress
        existing_progress = _load_progress(output)
        resume_download = False

        if existing_progress:
            if (
                existing_progress.get("url") == url
                and existing_progress.get("file_size") == file_size
            ):
                if existing_progress.get("parallel") == parallel:
                    print("Found existing download progress - checking chunks...")
                    resume_download = True
                else:
                    # Different parallelism - try smart remapping
                    old_parallel = existing_progress.get("parallel", 1)
                    print(
                        f"Found existing download with {old_parallel} parts, requested {parallel} parts"
                    )
                    print("Attempting smart chunk remapping...")

                    try:
                        # Only attempt remapping if we have range support and parallel > 1
                        if supports_ranges and parallel > 1:
                            remapped_chunks = _remap_chunks_for_different_parallelism(
                                existing_progress, parallel, file_size, output
                            )
                            if remapped_chunks:
                                # Create new progress with remapped chunks
                                existing_progress = {
                                    "url": url,
                                    "output": output,
                                    "file_size": file_size,
                                    "parallel": parallel,
                                    "completed_chunks": list(remapped_chunks),
                                    "timestamp": time.time(),
                                }
                                resume_download = True
                                print(
                                    f"Successfully remapped progress - resuming with {len(remapped_chunks)} chunks"
                                )
                            else:
                                print("No progress could be preserved - starting fresh")
                                _cleanup_progress(output)
                                _cleanup_orphaned_part_files(output, parallel)
                        else:
                            print(
                                "Single-threaded mode - cannot remap chunks, starting fresh"
                            )
                            _cleanup_progress(output)
                            _cleanup_orphaned_part_files(output, parallel)
                    except Exception as e:
                        print(f"Smart remapping failed: {e}")
                        print("Starting fresh download...")
                        _cleanup_progress(output)
                        _cleanup_orphaned_part_files(output, parallel)
                        existing_progress = None
            else:
                print(
                    "Previous download had different URL or file size - starting fresh"
                )
                _cleanup_progress(output)
                _cleanup_orphaned_part_files(output, parallel)

        # Show a preview loading bar
        if file_size > 0:
            print(f"Preparing to download {_format_size(file_size)}...")
            _show_preview_bar()
        else:
            print("File size unknown, starting download...")

        if not supports_ranges or parallel == 1:
            print("\nUsing single-threaded download...")
            _download_single_threaded(url, output, throttle_bps)
        else:
            print(f"\nUsing {parallel} parallel threads...")
            if throttle_bps:
                from .throttle import format_bandwidth

                total_limit = format_bandwidth(throttle_bps * parallel)
                print(
                    f"Total bandwidth limit: {total_limit} ({parallel} chunks × {format_bandwidth(throttle_bps)})"
                )
            if resume_download:
                print("Resuming previous download...")
            _download_parallel(
                url, output, file_size, parallel, existing_progress, throttle_bps
            )

        # Clean up progress tracking on successful completion
        _cleanup_progress(output)
        print(f"\nDownload completed: {output}")
        print(f"File successfully saved to: {os.path.abspath(output)}")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user. Progress saved for resuming.")
        raise
    except Exception as e:
        print(f"\nDownload failed: {str(e)}")
        print("Progress saved - you can resume this download later.")
        raise


def _get_file_info(url):
    """Get file information including size and range support."""

    # Detect if this is likely a media file from URL
    media_extensions = [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".webm",
        ".flv",
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
    ]
    is_media = any(ext in url.lower() for ext in media_extensions)

    try:
        print(".", end="", flush=True)

        # Try HEAD request with fallback
        with _make_request_with_fallback(
            url, method="HEAD", is_media=is_media, timeout=30
        ) as response:
            print(".", end="", flush=True)
            file_size = int(response.headers.get("Content-Length", 0))
            supports_ranges = response.headers.get("Accept-Ranges") == "bytes"

            # Extract filename from URL or Content-Disposition header
            filename = None
            content_disposition = response.headers.get("Content-Disposition", "")
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')

            if not filename:
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path) or "downloaded_file"

            print(".", end="", flush=True)
            return file_size, supports_ranges, filename

    except Exception as head_error:
        # If HEAD fails, try GET with Range header as fallback
        try:
            print(".", end="", flush=True)

            with _make_request_with_fallback(
                url,
                method="GET",
                range_header="bytes=0-0",
                is_media=is_media,
                timeout=30,
            ) as response:
                print(".", end="", flush=True)
                content_range = response.headers.get("Content-Range", "")
                if content_range:
                    file_size = int(content_range.split("/")[1])
                    supports_ranges = True
                else:
                    file_size = 0
                    supports_ranges = False

                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path) or "downloaded_file"

                print(".", end="", flush=True)
                return file_size, supports_ranges, filename

        except Exception:
            # If both HEAD and GET fail, re-raise the HEAD error
            raise head_error


def _download_single_threaded(url, output, throttle_bps=None):
    """Download file using single thread with resume support and optional throttling."""
    max_retries = 5

    # Detect if this is likely a media file
    media_extensions = [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".webm",
        ".flv",
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
    ]
    is_media = any(ext in output.lower() for ext in media_extensions)

    # Create throttle instance if needed
    throttle = None
    if throttle_bps:
        from .throttle import BandwidthThrottle

        throttle = BandwidthThrottle(throttle_bps)

    # Clean up any orphaned part files from previous parallel downloads
    _cleanup_orphaned_part_files(output, 1)

    for attempt in range(max_retries):
        try:
            # Check if partial file exists
            start_byte = 0
            if os.path.exists(output):
                start_byte = os.path.getsize(output)
                print(f"Resuming download from byte {start_byte}")

            # Use fallback system for single-threaded downloads
            fallbacks = get_user_agent_fallbacks(is_media)
            fallback_index = attempt % len(fallbacks)
            user_agent, description = fallbacks[fallback_index]

            if attempt > 0:
                print(f"Retry {attempt} with {description}...")

            # Create request with range header if resuming
            req = urllib.request.Request(url)
            if user_agent:
                req.add_header("User-Agent", user_agent)
            if start_byte > 0:
                req.add_header("Range", f"bytes={start_byte}-")

            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, timeout=30) as response:
                # Get total size (accounting for partial downloads)
                if start_byte > 0:
                    content_range = response.headers.get("Content-Range", "")
                    if content_range:
                        total_size = int(content_range.split("/")[1])
                    else:
                        total_size = start_byte + int(
                            response.headers.get("Content-Length", 0)
                        )
                else:
                    total_size = int(response.headers.get("Content-Length", 0))

                # Open in append mode if resuming, write mode if starting fresh
                mode = "ab" if start_byte > 0 else "wb"
                with open(output, mode) as f:
                    downloaded = start_byte

                    while True:
                        try:
                            chunk = response.read(
                                8192
                            )  # 8KB chunks for better throttling
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Apply throttling if enabled
                            if throttle:
                                throttle.throttle(len(chunk))

                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                _show_progress(progress, downloaded, total_size)
                        except (ConnectionError, TimeoutError) as e:
                            print(f"\nConnection error: {str(e)}")
                            raise  # Will retry with current progress

                print()  # New line after progress
                return  # Success

        except (HTTPError, URLError, ConnectionError, TimeoutError, OSError) as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Single-threaded download failed after {max_retries} attempts: {str(e)}"
                )

            delay = (2**attempt) + (attempt * 0.5)
            print(
                f"\nDownload failed (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

        except Exception as e:
            raise Exception(f"Single-threaded download failed: {str(e)}")


def _download_parallel(
    url, output, file_size, parallel, existing_progress=None, throttle_bps=None
):
    """Download file using multiple parallel threads with resume support."""
    chunk_size = file_size // parallel
    chunks = []
    completed_chunks = set()

    # If starting fresh (no existing progress), clean up any orphaned part files
    if not existing_progress:
        _cleanup_orphaned_part_files(output, parallel)

    # Create chunk ranges
    for i in range(parallel):
        start = i * chunk_size
        end = start + chunk_size - 1
        if i == parallel - 1:  # Last chunk gets remainder
            end = file_size - 1
        chunks.append((start, end, i))

    # Create temporary files for chunks
    temp_files = []
    for i in range(parallel):
        temp_file = f"{output}.part{i}"
        temp_files.append(temp_file)

    # Create throttle instances for each chunk (if throttling enabled)
    throttles = []
    if throttle_bps:
        from .throttle import BandwidthThrottle

        for _ in range(parallel):
            throttles.append(BandwidthThrottle(throttle_bps))
    else:
        throttles = [None] * parallel

    # Check existing progress and verify chunks
    if existing_progress:
        completed_chunks = set(existing_progress.get("completed_chunks", []))
        print(f"Verifying {len(completed_chunks)} completed chunks...")

        # Verify each supposedly completed chunk
        chunks_to_verify = list(completed_chunks)
        for chunk_id in chunks_to_verify:
            if chunk_id < len(chunks):
                start, end, _ = chunks[chunk_id]
                expected_size = end - start + 1
                temp_file = temp_files[chunk_id]

                if not _verify_chunk(temp_file, expected_size):
                    print(f"Chunk {chunk_id} corrupted, will re-download")
                    completed_chunks.discard(chunk_id)
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass

        if completed_chunks:
            print(f"{len(completed_chunks)} chunks verified and ready to resume")

    try:
        # Filter out completed chunks
        remaining_chunks = [
            (start, end, chunk_id)
            for start, end, chunk_id in chunks
            if chunk_id not in completed_chunks
        ]

        if not remaining_chunks:
            print("All chunks already completed!")
        else:
            print(f"Downloading {len(remaining_chunks)} remaining chunks...")

            # Initialize chunk progress tracking
            global chunk_progress
            chunk_progress = {}

            # Initialize progress for completed chunks
            for chunk_id in completed_chunks:
                if chunk_id < len(chunks):
                    start, end, _ = chunks[chunk_id]
                    chunk_size = end - start + 1
                    _update_chunk_progress(chunk_id, chunk_size, chunk_size)

            # Reserve space for progress display
            print("\n" * (parallel + 3))  # Space for chunk bars + overall bar

            # Start progress display thread
            display_active = True

            def progress_updater():
                while display_active:
                    _display_multi_chunk_progress(parallel, file_size)
                    time.sleep(0.5)  # Update twice per second

            progress_thread = threading.Thread(target=progress_updater, daemon=True)
            progress_thread.start()

            # Download remaining chunks in parallel with retry logic
            max_chunk_retries = 3
            failed_chunks = []

            for retry_round in range(max_chunk_retries):
                if retry_round > 0:
                    print(
                        f"\nRetrying {len(failed_chunks)} failed chunks (attempt {retry_round + 1}/{max_chunk_retries})..."
                    )
                    remaining_chunks = failed_chunks
                    failed_chunks = []

                if not remaining_chunks:
                    break

                with ThreadPoolExecutor(
                    max_workers=min(parallel, len(remaining_chunks))
                ) as executor:
                    future_to_chunk = {
                        executor.submit(
                            _download_chunk,
                            url,
                            start,
                            end,
                            temp_files[chunk_id],
                            chunk_id,
                            throttles[chunk_id],
                        ): (start, end, chunk_id)
                        for start, end, chunk_id in remaining_chunks
                    }

                    total_downloaded = sum(
                        os.path.getsize(temp_files[i])
                        for i in completed_chunks
                        if os.path.exists(temp_files[i])
                    )

                    for future in as_completed(future_to_chunk):
                        start, end, chunk_id = future_to_chunk[future]
                        try:
                            bytes_downloaded = future.result()
                            completed_chunks.add(chunk_id)
                            total_downloaded += bytes_downloaded

                            # Save progress after each completed chunk
                            _save_progress(
                                output, url, file_size, parallel, list(completed_chunks)
                            )

                        except Exception as e:
                            # Add failed chunk to retry list instead of failing immediately
                            print(f"\nChunk {chunk_id} failed: {str(e)}")
                            failed_chunks.append((start, end, chunk_id))

                            # Save progress even on failure
                            _save_progress(
                                output, url, file_size, parallel, list(completed_chunks)
                            )

            # If we still have failed chunks after all retries, raise an error
            if failed_chunks:
                failed_chunk_ids = [chunk_id for _, _, chunk_id in failed_chunks]
                raise Exception(
                    f"Failed to download chunks {failed_chunk_ids} after {max_chunk_retries} attempts"
                )

            # Stop progress display
            display_active = False
            time.sleep(0.6)  # Wait for final update

        print()  # New line after progress

        # Combine chunks into final file
        print("Combining chunks...")
        _combine_chunks(temp_files, output)

        # Clean up temporary files (but keep progress file until final cleanup)
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except OSError:
                pass

    except Exception:
        # Save progress on failure but keep temp files for resume
        _save_progress(output, url, file_size, parallel, list(completed_chunks))
        raise


def _download_chunk(url, start, end, temp_file, chunk_id=None, throttle=None):
    """Download a specific chunk of the file with progress reporting, resume capability, and optional throttling."""
    max_retries = 5  # Increased retries for network issues
    chunk_size = end - start + 1

    # Detect if this is likely a media file
    media_extensions = [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".webm",
        ".flv",
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
    ]
    is_media = any(ext in temp_file.lower() for ext in media_extensions)

    # Check if partial chunk already exists
    downloaded_offset = 0
    if os.path.exists(temp_file):
        downloaded_offset = os.path.getsize(temp_file)
        # Don't resume if file is corrupted or larger than expected
        if downloaded_offset > chunk_size:
            downloaded_offset = 0
            try:
                os.remove(temp_file)
            except OSError:
                pass

    for attempt in range(max_retries):
        try:
            # Calculate actual range to download (resume from partial)
            actual_start = start + downloaded_offset

            # If chunk is already complete, return immediately
            if downloaded_offset >= chunk_size:
                return chunk_size

            # Use fallback system for chunk downloads (but don't show verbose output)
            # We'll try each User-Agent once per retry attempt
            fallbacks = get_user_agent_fallbacks(is_media)
            fallback_index = attempt % len(fallbacks)
            user_agent, _ = fallbacks[fallback_index]

            req = urllib.request.Request(url)
            if user_agent:
                req.add_header("User-Agent", user_agent)
            req.add_header("Range", f"bytes={actual_start}-{end}")

            # Add timeout to prevent hanging
            with urllib.request.urlopen(req, timeout=30) as response:
                # Open in append mode if resuming, write mode if starting fresh
                mode = "ab" if downloaded_offset > 0 else "wb"
                with open(temp_file, mode) as f:
                    downloaded_this_session = 0
                    while True:
                        try:
                            chunk = response.read(
                                8192
                            )  # 8KB chunks for better throttling
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded_this_session += len(chunk)
                            total_downloaded = (
                                downloaded_offset + downloaded_this_session
                            )

                            # Apply throttling if enabled
                            if throttle:
                                throttle.throttle(len(chunk))

                            # Update chunk progress if tracking is enabled
                            if chunk_id is not None:
                                _update_chunk_progress(
                                    chunk_id, total_downloaded, chunk_size
                                )

                        except (ConnectionError, TimeoutError) as e:
                            # Network error during chunk read - partial progress is saved
                            print(f"\nNetwork error in chunk {chunk_id}: {str(e)}")
                            downloaded_offset += downloaded_this_session
                            raise  # Will retry from new offset

                    return downloaded_offset + downloaded_this_session

        except (HTTPError, URLError, ConnectionError, TimeoutError, OSError) as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"Chunk {chunk_id} download failed after {max_retries} attempts: {str(e)}"
                )

            # Update offset for next retry attempt if we have a partial file
            if os.path.exists(temp_file):
                downloaded_offset = os.path.getsize(temp_file)

            # Exponential backoff with jitter for network errors
            delay = (2**attempt) + (attempt * 0.5)  # 1, 2.5, 5, 9.5, 16 seconds
            print(
                f"\nChunk {chunk_id} failed (attempt {attempt + 1}/{max_retries}), retrying in {delay:.1f}s..."
            )
            time.sleep(delay)

        except Exception as e:
            # Non-network errors - don't preserve partial downloads
            if attempt == max_retries - 1:
                raise Exception(
                    f"Chunk {chunk_id} download failed after {max_retries} attempts: {str(e)}"
                )
            time.sleep(1 * (attempt + 1))  # Basic backoff for other errors


def _combine_chunks(temp_files, output):
    """Combine downloaded chunks into final file."""
    with open(output, "wb") as outfile:
        for temp_file in temp_files:
            with open(temp_file, "rb") as infile:
                while True:
                    chunk = infile.read(8192)
                    if not chunk:
                        break
                    outfile.write(chunk)


def _show_preview_bar():
    """Show a preview loading bar animation."""
    import time

    print("Initializing download...")
    bar_chars = ["░", "█"]
    for i in range(20):
        bar = "".join(bar_chars[1] if j <= i else bar_chars[0] for j in range(20))
        percentage = ((i + 1) / 20) * 100
        sys.stdout.write(f"\rPreparing: [{bar}] {percentage:.0f}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print()  # New line after preview


def _show_progress(progress, downloaded, total):
    """Display download progress with speed and ETA."""
    bar_length = 50
    filled_length = int(bar_length * progress / 100)

    # Create a more visible progress bar with different characters
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    downloaded_str = _format_size(downloaded)
    total_str = _format_size(total)

    # Initialize timing data if not present
    if not hasattr(_show_progress, "start_time"):
        _show_progress.start_time = time.time()
        _show_progress.last_time = time.time()
        _show_progress.last_downloaded = 0

    current_time = time.time()

    # Calculate speed and ETA
    speed_str = ""
    eta_str = ""

    # Calculate overall average speed
    total_time = current_time - _show_progress.start_time
    if total_time > 0:
        avg_speed = downloaded / total_time
        if avg_speed > 0:
            speed_str = f" | {_format_size(avg_speed)}/s"

            # Calculate ETA
            remaining_bytes = total - downloaded
            eta_seconds = remaining_bytes / avg_speed
            if eta_seconds < 60:
                eta_str = f" | ETA: {eta_seconds:.0f}s"
            elif eta_seconds < 3600:
                eta_str = f" | ETA: {eta_seconds/60:.0f}m {eta_seconds%60:.0f}s"
            else:
                hours = eta_seconds // 3600
                minutes = (eta_seconds % 3600) // 60
                eta_str = f" | ETA: {hours:.0f}h {minutes:.0f}m"

    # Enhanced progress display with speed and ETA
    progress_text = f"\r[{bar}] {progress:.1f}% ({downloaded_str}/{total_str}){speed_str}{eta_str}   "

    sys.stdout.write(progress_text)
    sys.stdout.flush()


def _format_size(bytes_size):
    """Format bytes into human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def _update_chunk_progress(chunk_id, downloaded, total):
    """Update progress for a specific chunk."""
    with progress_lock:
        chunk_progress[chunk_id] = {
            "downloaded": downloaded,
            "total": total,
            "progress": (downloaded / total * 100) if total > 0 else 0,
        }


def _display_multi_chunk_progress(total_chunks, file_size):
    """Display progress bars for all chunks."""
    with progress_lock:
        # Clear the screen area for chunk progress
        sys.stdout.write(f"\r\033[{total_chunks + 2}A")  # Move cursor up

        # Calculate overall progress
        total_downloaded = 0
        overall_progress = 0

        for chunk_id in range(total_chunks):
            if chunk_id in chunk_progress:
                chunk_data = chunk_progress[chunk_id]
                downloaded = chunk_data["downloaded"]
                total = chunk_data["total"]
                progress = chunk_data["progress"]
                total_downloaded += downloaded

                # Create mini progress bar for this chunk
                bar_length = 20
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                status = "DONE" if progress >= 100 else "DOWN"
                print(
                    f"Chunk {chunk_id:2d}: {status} [{bar}] {progress:5.1f}% {_format_size(downloaded):>8}/{_format_size(total):<8}"
                )
            else:
                # Chunk not started yet
                bar = "░" * 20
                print(f"Chunk {chunk_id:2d}: WAIT [{bar}]   0.0%     0 B/    0 B    ")

        # Overall progress
        if file_size > 0:
            overall_progress = (total_downloaded / file_size) * 100

        print("─" * 70)
        overall_bar_length = 50
        overall_filled = int(overall_bar_length * overall_progress / 100)
        overall_bar = "█" * overall_filled + "░" * (overall_bar_length - overall_filled)

        print(
            f"Overall: [{overall_bar}] {overall_progress:.1f}% ({_format_size(total_downloaded)}/{_format_size(file_size)})"
        )

        sys.stdout.flush()
