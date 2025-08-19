"""
QuickDownload - High-performance parallel file downloader with torrent and queue support

A command-line tool and Python library for downloading files with parallel connections,
resume capabilities, streaming mode, and queue management.
"""

__version__ = "1.2.0"
__author__ = "Nikhil K Singh"
__email__ = "nsr.nikhilsingh@gmail.com"

from .utils import download_file
from .torrent_utils import download_torrent, is_torrent_url
from .queue_manager import (
    QueueManager,
    DownloadJob,
    queue_add,
    queue_start,
    queue_stop,
    queue_list,
    queue_remove,
    queue_clear,
    queue_status,
)

__all__ = [
    "download_file",
    "download_torrent",
    "is_torrent_url",
    "QueueManager",
    "DownloadJob",
    "queue_add",
    "queue_start",
    "queue_stop",
    "queue_list",
    "queue_remove",
    "queue_clear",
    "queue_status",
]
