#!/usr/bin/env python3

import argparse
import sys

from .utils import download_file
from .torrent_utils import download_torrent, is_torrent_url
from .queue_manager import (
    queue_add,
    queue_start,
    queue_stop,
    queue_list,
    queue_remove,
    queue_clear,
    queue_status,
)


def is_magnet_link(url: str) -> bool:
    """Check if URL is a magnet link."""
    return url.startswith("magnet:")


def main():
    parser = argparse.ArgumentParser(
        description="QuickDownload - High-performance parallel file downloader with queue support"
    )

    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Direct download command (default)
    download_parser = subparsers.add_parser(
        "download", help="Download a file directly", add_help=False
    )
    download_parser.add_argument("url", help="URL to download")
    download_parser.add_argument("-o", "--output", help="Output filename")
    download_parser.add_argument(
        "-p",
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel connections (default: 4)",
    )
    download_parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming mode for real-time playback",
    )
    download_parser.add_argument(
        "--buffer",
        type=int,
        default=30,
        help="Buffer time in seconds for streaming mode (default: 30)",
    )
    download_parser.add_argument(
        "--seed-time",
        type=int,
        default=0,
        help="Time to seed after download (minutes, torrent only)",
    )
    download_parser.add_argument(
        "--throttle", type=str, help="Bandwidth limit per chunk (e.g., 1M, 500k, 30K)"
    )
    download_parser.add_argument(
        "--no-speed-boost",
        action="store_true",
        help="Disable aggressive speed optimizations for torrents",
    )

    # Queue management commands
    queue_parser = subparsers.add_parser("queue", help="Manage download queue")
    queue_subparsers = queue_parser.add_subparsers(
        dest="queue_action", help="Queue actions"
    )

    # queue add
    add_parser = queue_subparsers.add_parser("add", help="Add download to queue")
    add_parser.add_argument("url", help="URL to download")
    add_parser.add_argument("-o", "--output", help="Output filename")
    add_parser.add_argument(
        "-p",
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel connections (default: 4)",
    )
    add_parser.add_argument(
        "--stream", action="store_true", help="Enable streaming mode"
    )
    add_parser.add_argument(
        "--buffer",
        type=int,
        default=30,
        help="Buffer time in seconds for streaming mode",
    )
    add_parser.add_argument(
        "--throttle", type=str, help="Bandwidth limit per chunk (e.g., 1M, 500k, 30K)"
    )

    # queue start
    start_parser = queue_subparsers.add_parser("start", help="Start processing queue")
    start_parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per job (default: 3)",
    )

    # queue list
    queue_subparsers.add_parser("list", help="List all jobs in queue")

    # queue status
    queue_subparsers.add_parser("status", help="Show queue status")

    # queue remove
    remove_parser = queue_subparsers.add_parser("remove", help="Remove job from queue")
    remove_parser.add_argument("job_id", help="Job ID to remove")

    # queue clear
    clear_parser = queue_subparsers.add_parser("clear", help="Clear queue")
    clear_parser.add_argument(
        "--completed", action="store_true", help="Clear only completed jobs"
    )

    # queue stop
    queue_subparsers.add_parser("stop", help="Stop queue processing")

    # Cluster management commands
    cluster_parser = subparsers.add_parser("cluster", help="Manage cluster downloading")
    cluster_subparsers = cluster_parser.add_subparsers(
        dest="cluster_action", help="Cluster actions"
    )

    # cluster init
    cluster_subparsers.add_parser("init", help="Initialize cluster node")

    # cluster set
    set_parser = cluster_subparsers.add_parser("set", help="Set node name")
    set_parser.add_argument("name", help="Node name to set")

    # cluster download
    cluster_download_parser = cluster_subparsers.add_parser(
        "download", help="Start cluster download"
    )
    cluster_download_parser.add_argument("url", help="URL to download")
    cluster_download_parser.add_argument("-o", "--output", help="Output filename")
    cluster_download_parser.add_argument(
        "-p",
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel connections (default: 4)",
    )
    cluster_download_parser.add_argument(
        "--throttle", type=str, help="Bandwidth limit per chunk (e.g., 1M, 500k)"
    )
    cluster_download_parser.add_argument(
        "--required-nodes",
        type=int,
        default=2,
        help="Minimum required nodes (default: 2)",
    )
    cluster_download_parser.add_argument(
        "--wait-time",
        type=int,
        default=60,
        help="Wait time for node registration in seconds (default: 60)",
    )

    # cluster register
    register_parser = cluster_subparsers.add_parser(
        "register", help="Register for download session"
    )
    register_parser.add_argument("session_id", help="Session ID to register for")

    # cluster unregister
    unregister_parser = cluster_subparsers.add_parser(
        "unregister", help="Unregister from download session"
    )
    unregister_parser.add_argument("session_id", help="Session ID to unregister from")

    # cluster withdraw
    cluster_subparsers.add_parser("withdraw", help="Withdraw from all sessions")

    # cluster status
    cluster_subparsers.add_parser("status", help="Show cluster status")

    # Handle case where no subcommand is provided (direct download)
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    # If first argument is not a subcommand, treat as direct download
    if len(sys.argv) >= 2 and sys.argv[1] not in ["queue", "download", "cluster"]:
        # Insert 'download' as first argument to make it a download command
        sys.argv.insert(1, "download")

    args = parser.parse_args()

    try:
        if args.command == "download" or args.command is None:
            # Validate throttle parameter if provided
            if hasattr(args, "throttle") and args.throttle:
                try:
                    from .throttle import parse_bandwidth_limit

                    parse_bandwidth_limit(args.throttle)  # Validate format
                except ValueError as e:
                    print(f"Error: {e}")
                    return 1

            # Direct download mode
            if hasattr(args, "url"):
                if is_magnet_link(args.url) or is_torrent_url(args.url):
                    if args.stream:
                        print("Warning: Streaming mode not supported for torrents")
                    if hasattr(args, "throttle") and args.throttle:
                        print("Warning: Throttling not supported for torrents")
                    
                    # Enable high-speed mode by default, disable only if --no-speed-boost is used
                    high_speed = not getattr(args, "no_speed_boost", False)
                    if high_speed:
                        print("Speed boost enabled for faster downloads")
                    
                    download_torrent(
                        args.url, 
                        args.output, 
                        getattr(args, "seed_time", 0),
                        high_speed=high_speed
                    )
                elif args.stream:
                    try:
                        from .streaming import download_streaming

                        throttle_limit = getattr(args, "throttle", None)
                        download_streaming(
                            args.url,
                            args.output,
                            args.parallel,
                            args.buffer,
                            throttle_limit,
                        )
                    except ImportError:
                        print(
                            "Warning: Streaming mode not available, falling back to regular download"
                        )
                        throttle_limit = getattr(args, "throttle", None)
                        download_file(
                            args.url, args.output, args.parallel, throttle_limit
                        )
                else:
                    throttle_limit = getattr(args, "throttle", None)
                    download_file(args.url, args.output, args.parallel, throttle_limit)
            else:
                parser.print_help()

        elif args.command == "queue":
            # Queue management mode
            if args.queue_action == "add":
                # Validate throttle parameter if provided
                if hasattr(args, "throttle") and args.throttle:
                    try:
                        from .throttle import parse_bandwidth_limit

                        parse_bandwidth_limit(args.throttle)  # Validate format
                    except ValueError as e:
                        print(f"Error: {e}")
                        return 1

                throttle_limit = getattr(args, "throttle", None)
                queue_add(
                    args.url,
                    args.output,
                    args.parallel,
                    args.stream,
                    args.buffer,
                    throttle_limit,
                )

            elif args.queue_action == "start":
                queue_start(args.max_retries)

            elif args.queue_action == "list":
                queue_list()

            elif args.queue_action == "status":
                queue_status()

            elif args.queue_action == "remove":
                queue_remove(args.job_id)

            elif args.queue_action == "clear":
                queue_clear(args.completed)

            elif args.queue_action == "stop":
                queue_stop()

            else:
                queue_parser.print_help()

        elif args.command == "cluster":
            # Cluster management mode
            from .cluster import (
                init_cluster,
                set_node_name,
                cluster_download,
                register_for_session,
                unregister_from_session,
                withdraw_all,
                show_status,
            )

            if args.cluster_action == "init":
                if init_cluster():
                    print("✓ Cluster node initialized successfully")
                else:
                    print("✗ Failed to initialize cluster node")
                    return 1

            elif args.cluster_action == "set":
                set_node_name(args.name)

            elif args.cluster_action == "download":
                # Validate throttle parameter if provided
                if hasattr(args, "throttle") and args.throttle:
                    try:
                        from .throttle import parse_bandwidth_limit

                        parse_bandwidth_limit(args.throttle)  # Validate format
                    except ValueError as e:
                        print(f"Error: {e}")
                        return 1

                try:
                    session_id = cluster_download(
                        args.url,
                        args.output,
                        args.parallel,
                        getattr(args, "throttle", None),
                        args.required_nodes,
                        args.wait_time,
                    )
                    print(f"✓ Cluster download session: {session_id}")
                except Exception as e:
                    print(f"✗ Failed to start cluster download: {e}")
                    return 1

            elif args.cluster_action == "register":
                if register_for_session(args.session_id):
                    print("✓ Successfully registered for session")
                else:
                    print("✗ Failed to register for session")
                    return 1

            elif args.cluster_action == "unregister":
                if unregister_from_session(args.session_id):
                    print("✓ Successfully unregistered from session")
                else:
                    print("✗ Failed to unregister from session")
                    return 1

            elif args.cluster_action == "withdraw":
                withdraw_all()

            elif args.cluster_action == "status":
                show_status()

            else:
                cluster_parser.print_help()
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
