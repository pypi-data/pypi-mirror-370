"""
Torrent download utilities for QuickDownload.

This module provides functionality to download torrents using magnet links,
.torrent files, or .torrent URLs using the libtorrent library.
"""

import os
import sys
import time
import tempfile
import urllib.request

try:
    import libtorrent as lt

    LIBTORRENT_AVAILABLE = True
except ImportError:
    LIBTORRENT_AVAILABLE = False


def is_torrent_url(url):
    """
    Check if URL is a torrent file or magnet link.

    Args:
        url (str): The URL or file path to check

    Returns:
        bool: True if it's a torrent-related URL/file
    """
    return (
        url.startswith("magnet:")
        or url.endswith(".torrent")
        or (os.path.isfile(url) and url.endswith(".torrent"))
    )


def check_libtorrent():
    """
    Check if libtorrent is available and provide helpful error message.

    Raises:
        ImportError: If libtorrent is not available
    """
    if not LIBTORRENT_AVAILABLE:
        print("Error: libtorrent is required for torrent downloads.")
        print("Install it with: pip install libtorrent")
        print("Or on macOS: brew install libtorrent-rasterbar")
        sys.exit(1)


def download_torrent_file(url):
    """
    Download a .torrent file from URL to a temporary file.

    Args:
        url (str): URL to the .torrent file

    Returns:
        str: Path to the downloaded temporary .torrent file
    """
    print(f"Downloading .torrent file from: {url}")
    temp_file = tempfile.NamedTemporaryFile(suffix=".torrent", delete=False)
    try:
        urllib.request.urlretrieve(url, temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Error downloading .torrent file: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise


def format_size(bytes_size):
    """
    Format bytes as human readable string.

    Args:
        bytes_size (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if bytes_size == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_time(seconds):
    """
    Format seconds as human readable time string.

    Args:
        seconds (int): Time in seconds

    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def download_torrent(torrent_input, output_dir=None, seed_time=0, high_speed=True):
    """
    Download a torrent file or magnet link with speed optimizations.

    Args:
        torrent_input (str): Path to .torrent file, magnet link, or URL to .torrent
        output_dir (str): Directory to save downloaded files (default: current directory)
        seed_time (int): Time to seed in minutes after download completes (default: 0)
        high_speed (bool): Enable aggressive speed optimizations (default: True)
    """
    check_libtorrent()

    if output_dir is None:
        output_dir = os.getcwd()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("QuickDownload - Torrent Mode")
    print(f"Output directory: {output_dir}")
    print("=" * 50)

    # Create libtorrent session with aggressive speed optimization settings
    settings = {
        # Basic settings
        "user_agent": "QuickDownload/1.1",
        "listen_interfaces": "0.0.0.0:6881,[::]:6881",  # IPv4 + IPv6
        
        # Peer discovery and connectivity
        "enable_dht": True,
        "enable_lsd": True,  # Local Service Discovery
        "enable_upnp": True,
        "enable_natpmp": True,
        "enable_incoming_utp": True,
        "enable_outgoing_utp": True,
        
        # Connection limits (aggressive for speed)
        "connections_limit": 500,  # Max total connections
        "connections_limit_factor": 150,  # Connections per torrent factor
        "half_open_limit": 50,  # Max half-open connections
        "max_peerlist_size": 4000,  # Larger peer list
        
        # Download optimization
        "max_queued_disk_bytes": 16 * 1024 * 1024,  # 16MB disk queue
        "cache_size": 512,  # 512 * 16KB = 8MB cache
        "read_cache_line_size": 64,  # Larger read cache lines
        "write_cache_line_size": 64,  # Larger write cache lines
        "cache_buffer_chunk_size": 128,  # Optimize cache chunks
        "use_read_cache": True,
        "coalesce_reads": True,
        "coalesce_writes": True,
        
        # Piece selection and requesting
        "piece_timeout": 20,  # Faster piece timeout
        "request_timeout": 15,  # Faster request timeout
        "max_out_request_queue": 1500,  # More requests in flight
        "max_allowed_in_request_queue": 2000,
        "whole_pieces_threshold": 20,  # Download whole pieces threshold
        
        # Bandwidth and choking
        "choking_algorithm": 2,  # Rate-based choking (fastest)
        "seed_choking_algorithm": 1,  # Fastest upload choking
        "mixed_mode_algorithm": 0,  # Prefer downloading peers
        "upload_rate_limit": 0,  # No upload limit (be generous to get better download)
        "download_rate_limit": 0,  # No download limit
        
        # Advanced optimizations
        "prefer_udp_trackers": True,
        "strict_super_seeding": False,
        "allow_multiple_connections_per_ip": True,
        "send_buffer_watermark": 1024 * 1024,  # 1MB send buffer
        "send_buffer_low_watermark": 512 * 1024,  # 512KB low watermark
        "send_buffer_watermark_factor": 150,
        
        # Tracker and DHT optimization
        "auto_manage_startup": 60,  # Quick startup
        "max_failcount": 1,  # Quick failure recovery
        "tracker_completion_timeout": 20,
        "tracker_receive_timeout": 15,
        "dht_announce_interval": 900,  # 15 min DHT announces
        
        # Encryption (can help with ISP throttling)
        "out_enc_policy": 1,  # Enable outgoing encryption
        "in_enc_policy": 1,   # Enable incoming encryption
        "allowed_enc_level": 2,  # Both plaintext and encrypted
        "prefer_rc4": True,
    }

    session = lt.session(settings)

    temp_torrent_file = None

    try:
        # Add torrent based on input type with speed optimizations
        add_params = {
            "save_path": output_dir,
            "flags": (
                lt.torrent_flags.auto_managed |
                lt.torrent_flags.duplicate_is_error |
                lt.torrent_flags.apply_ip_filter
            )
        }
        
        # Add speed optimization flags if high_speed mode is enabled
        if high_speed:
            add_params["flags"] |= (
                lt.torrent_flags.sequential_download |
                lt.torrent_flags.super_seeding
            )
            # More aggressive settings for this specific torrent
            add_params.update({
                "max_connections": 100,  # Max connections for this torrent
                "max_uploads": 50,       # Max uploads for better ratio
                "upload_limit": -1,      # No upload limit
                "download_limit": -1,    # No download limit
            })
        
        if torrent_input.startswith("magnet:"):
            print("Adding magnet link...")
            handle = lt.add_magnet_uri(session, torrent_input, add_params)
        elif torrent_input.startswith("http"):
            print("Downloading and adding .torrent file...")
            temp_torrent_file = download_torrent_file(torrent_input)
            info = lt.torrent_info(temp_torrent_file)
            add_params["ti"] = info
            handle = session.add_torrent(add_params)
        else:
            print(f"Loading .torrent file: {torrent_input}")
            if not os.path.exists(torrent_input):
                raise FileNotFoundError(f"Torrent file not found: {torrent_input}")
            info = lt.torrent_info(torrent_input)
            add_params["ti"] = info
            handle = session.add_torrent(add_params)

        # Wait for metadata (especially important for magnet links)
        print("Waiting for metadata...", end="", flush=True)
        metadata_timeout = 60  # 60 seconds timeout
        start_time = time.time()
        dots_count = 0

        while not handle.has_metadata():
            if time.time() - start_time > metadata_timeout:
                raise TimeoutError("Timeout waiting for torrent metadata")
            
            # Create animated dots (max 6 dots, then reset)
            dots_count = (dots_count + 1) % 7
            dots = "." * dots_count + " " * (6 - dots_count)
            elapsed = time.time() - start_time
            print(f"\rWaiting for metadata{dots} ({elapsed:.0f}s)", end="", flush=True)
            time.sleep(1)

        print("\nMetadata received!")
        print(f"Torrent name: {handle.name()}")
        print(f"Total size: {format_size(handle.status().total_wanted)}")
        print(f"Files: {handle.get_torrent_info().num_files()}")
        
        # Apply additional speed optimizations after metadata is available
        if high_speed:
            print("Applying speed optimizations...")
            # Force the torrent to be active and start downloading immediately
            handle.resume()
            handle.set_priority(255)  # Highest priority
            
            # Set piece priorities for faster start (prioritize first/last pieces)
            torrent_info = handle.get_torrent_info()
            if torrent_info.num_pieces() > 0:
                # Prioritize first and last few pieces for faster startup
                for i in range(min(5, torrent_info.num_pieces())):
                    handle.piece_priority(i, 7)  # Highest piece priority
                for i in range(max(0, torrent_info.num_pieces() - 5), torrent_info.num_pieces()):
                    handle.piece_priority(i, 7)  # Highest piece priority
        
        print("=" * 50)

        # Download loop
        print("Starting download...")
        last_progress = -1.0
        last_update_time = 0
        start_download_time = time.time()

        while not handle.is_seed():
            status = handle.status()

            # Calculate progress and stats
            progress = status.progress * 100
            download_rate = status.download_rate / 1024  # KB/s
            upload_rate = status.upload_rate / 1024
            downloaded = status.total_done
            total_size = status.total_wanted
            num_peers = status.num_peers
            num_seeds = status.num_seeds

            # Calculate ETA
            if download_rate > 0:
                remaining_bytes = total_size - downloaded
                eta_seconds = remaining_bytes / (download_rate * 1024)
                eta_str = format_time(eta_seconds)
            else:
                eta_str = "∞"

            # Update progress in real-time with smart throttling
            # Update immediately if progress changed, but limit to reasonable frequency
            current_time = time.time()
            time_since_last_update = current_time - last_update_time
            progress_changed = abs(progress - last_progress) >= 0.05  # More sensitive: 0.05%
            
            should_update = (
                progress_changed or  # Any significant progress change
                time_since_last_update >= 0.8 or  # Force update every 0.8 seconds for live stats
                last_progress < 0  # First update
            )
            
            if should_update:
                # Create progress bar for torrent download
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                # Print progress with proper line clearing
                progress_line = (
                    f"[{bar}] {progress:.1f}% | "
                    f"{format_size(downloaded)}/{format_size(total_size)} | "
                    f"↓{download_rate:.1f} KB/s ↑{upload_rate:.1f} KB/s | "
                    f"Peers: {num_peers} Seeds: {num_seeds} | "
                    f"ETA: {eta_str}"
                )
                
                # Clear line and print (ensure we clear enough space)
                print(f"\r{' ' * 120}", end="", flush=True)
                print(f"\r{progress_line}", end="", flush=True)
                
                last_progress = progress
                last_update_time = current_time

            time.sleep(1)

        download_time = time.time() - start_download_time
        print(f"\n{'=' * 50}")
        print(f"Download completed: {handle.name()}")
        print(f"Time taken: {format_time(download_time)}")
        print(
            f"Average speed: {format_size(handle.status().total_wanted / download_time)}/s"
        )

        # Seed for specified time
        if seed_time > 0:
            print(f"\nSeeding for {seed_time} minutes...")
            seed_end = time.time() + (seed_time * 60)
            total_seed_time = seed_time * 60

            while time.time() < seed_end:
                status = handle.status()
                upload_rate = status.upload_rate / 1024
                uploaded = status.total_upload
                remaining_time = seed_end - time.time()
                elapsed_time = total_seed_time - remaining_time

                # Create seeding progress bar
                seed_progress = (elapsed_time / total_seed_time) * 100
                bar_length = 20
                filled_length = int(bar_length * seed_progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"\rSeeding [{bar}] {seed_progress:.1f}% | "
                    f"↑{upload_rate:.1f} KB/s | "
                    f"Uploaded: {format_size(uploaded)} | "
                    f"Time left: {format_time(remaining_time)}",
                    end="",
                    flush=True,
                )
                time.sleep(1)

            print("\nSeeding completed.")

        print(f"Files saved to: {output_dir}")

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during torrent download: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary torrent file
        if temp_torrent_file and os.path.exists(temp_torrent_file):
            os.unlink(temp_torrent_file)
