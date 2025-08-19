"""
Queue management system for QuickDownload.
Handles adding, removing, and processing download jobs.
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

from .utils import download_file
from .torrent_utils import download_torrent, is_torrent_url


@dataclass
class DownloadJob:
    """Represents a single download job in the queue."""

    id: str
    url: str
    output: Optional[str] = None
    parallel: int = 4
    streaming: bool = False
    buffer_seconds: int = 30
    throttle_limit: Optional[str] = None  # New field for bandwidth limit
    status: str = "pending"  # pending, downloading, completed, failed, paused
    added_time: str = ""
    started_time: Optional[str] = None
    completed_time: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    progress: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DownloadJob":
        """Create job from dictionary."""
        return cls(**data)


class QueueManager:
    """Manages download queue with persistent storage."""

    def __init__(self, queue_file: Optional[str] = None):
        """Initialize queue manager."""
        if queue_file is None:
            # Default queue file in user's home directory
            home = Path.home()
            self.queue_dir = home / ".quickdownload"
            self.queue_dir.mkdir(exist_ok=True)
            self.queue_file = self.queue_dir / "queue.json"
        else:
            self.queue_file = Path(queue_file)
            self.queue_dir = self.queue_file.parent
            self.queue_dir.mkdir(exist_ok=True)

        self.jobs: List[DownloadJob] = []
        self.current_job: Optional[DownloadJob] = None
        self.is_running = False
        self.should_stop = False
        self.download_thread: Optional[threading.Thread] = None

        # Load existing queue
        self._load_queue()

    def _load_queue(self):
        """Load queue from persistent storage."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r") as f:
                    data = json.load(f)
                    self.jobs = [
                        DownloadJob.from_dict(job_data)
                        for job_data in data.get("jobs", [])
                    ]
                print(f"Loaded {len(self.jobs)} jobs from queue")
            except Exception as e:
                print(f"Warning: Could not load queue file: {e}")
                self.jobs = []
        else:
            self.jobs = []

    def _save_queue(self):
        """Save queue to persistent storage."""
        try:
            data = {
                "jobs": [job.to_dict() for job in self.jobs],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.queue_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save queue: {e}")

    def add_job(
        self,
        url: str,
        output: Optional[str] = None,
        parallel: int = 4,
        streaming: bool = False,
        buffer_seconds: int = 30,
        throttle_limit: Optional[str] = None,
    ) -> str:
        """Add a new download job to the queue."""

        # Generate unique job ID
        job_id = f"job_{int(time.time())}_{len(self.jobs)}"

        # Auto-detect filename if not provided
        if output is None:
            try:
                output = url.split("/")[-1].split("?")[0] or f"download_{job_id}"
            except Exception:
                output = f"download_{job_id}"

        job = DownloadJob(
            id=job_id,
            url=url,
            output=output,
            parallel=parallel,
            streaming=streaming,
            buffer_seconds=buffer_seconds,
            throttle_limit=throttle_limit,
            added_time=datetime.now().isoformat(),
        )

        self.jobs.append(job)
        self._save_queue()

        print(f"Added job {job_id}: {url}")
        if output:
            print(f"  Output: {output}")
        print(f"  Parallel: {parallel}")
        if streaming:
            print(f"  Streaming: enabled ({buffer_seconds}s buffer)")
        if throttle_limit:
            print(f"  Throttle: {throttle_limit} per chunk")

        return job_id

    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        for i, job in enumerate(self.jobs):
            if job.id == job_id:
                if job.status == "downloading":
                    print(f"Cannot remove job {job_id}: currently downloading")
                    return False

                self.jobs.pop(i)
                self._save_queue()
                print(f"Removed job {job_id}")
                return True

        print(f"Job {job_id} not found")
        return False

    def list_jobs(self):
        """Display all jobs in the queue."""
        if not self.jobs:
            print("Queue is empty")
            return

        print(f"\nDownload Queue ({len(self.jobs)} jobs):")
        print("=" * 80)

        for job in self.jobs:
            status_emoji = {
                "pending": "⏳",
                "downloading": "⬇️",
                "completed": "✅",
                "failed": "❌",
                "paused": "⏸️",
            }.get(job.status, "❓")

            print(f"{status_emoji} {job.id}")
            print(f"   URL: {job.url}")
            print(f"   Output: {job.output}")
            print(f"   Parallel: {job.parallel}")
            if job.streaming:
                print(f"   Streaming: enabled ({job.buffer_seconds}s buffer)")
            if job.throttle_limit:
                print(f"   Throttle: {job.throttle_limit} per chunk")
            print(f"   Status: {job.status}")
            if job.progress > 0:
                print(f"   Progress: {job.progress:.1f}%")
            if job.error_message:
                print(f"   Error: {job.error_message}")
            print(f"   Added: {job.added_time}")
            print()

    def clear_completed(self):
        """Remove all completed jobs from the queue."""
        completed_count = len([j for j in self.jobs if j.status == "completed"])
        self.jobs = [job for job in self.jobs if job.status != "completed"]
        self._save_queue()
        print(f"Removed {completed_count} completed jobs")

    def clear_all(self):
        """Clear entire queue."""
        if self.is_running:
            print("Cannot clear queue while downloads are running")
            return False

        job_count = len(self.jobs)
        self.jobs = []
        self._save_queue()
        print(f"Cleared {job_count} jobs from queue")
        return True

    def start_queue(self, max_retries: int = 3):
        """Start processing the download queue."""
        if self.is_running:
            print("Queue is already running")
            return

        pending_jobs = [job for job in self.jobs if job.status == "pending"]
        if not pending_jobs:
            print("No pending jobs in queue")
            return

        print(f"Starting download queue ({len(pending_jobs)} pending jobs)")
        print("Press Ctrl+C to stop the queue\n")

        self.is_running = True
        self.should_stop = False

        try:
            for job in pending_jobs:
                if self.should_stop:
                    print("\nQueue stopped by user")
                    break

                self.current_job = job
                self._process_job(job, max_retries)
                self.current_job = None

                # Small delay between jobs
                if not self.should_stop:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\nQueue interrupted by user")
            if self.current_job:
                self.current_job.status = "paused"

        finally:
            self.is_running = False
            self.current_job = None
            self._save_queue()
            print("Queue processing stopped")

    def _process_job(self, job: DownloadJob, max_retries: int):
        """Process a single download job."""
        print(f"Processing job {job.id}")
        print(f"URL: {job.url}")
        print(f"Output: {job.output}")
        print(f"Parallel: {job.parallel}")
        if job.streaming:
            print(f"Streaming: enabled ({job.buffer_seconds}s buffer)")
        if job.throttle_limit:
            print(f"Throttle: {job.throttle_limit} per chunk")
        print("-" * 60)

        job.status = "downloading"
        job.started_time = datetime.now().isoformat()
        self._save_queue()

        success = False
        for attempt in range(max_retries):
            try:
                if self.should_stop:
                    job.status = "paused"
                    return

                if attempt > 0:
                    print(f"Retry attempt {attempt + 1}/{max_retries}")

                # Check if it's a magnet link or torrent
                def is_magnet_link(url: str) -> bool:
                    return url.startswith("magnet:")

                # Choose download method
                if is_magnet_link(job.url) or is_torrent_url(job.url):
                    if job.streaming:
                        print("Warning: Streaming mode not supported for torrents")
                    if job.throttle_limit:
                        print("Warning: Throttling not supported for torrents")
                    download_torrent(job.url, job.output)
                    success = True  # If no exception was raised, it succeeded
                elif job.streaming:
                    # Import streaming function here to avoid circular imports
                    try:
                        from .streaming import download_streaming

                        download_streaming(
                            job.url,
                            job.output,
                            job.parallel,
                            job.buffer_seconds,
                            job.throttle_limit,
                        )
                        success = True  # If no exception was raised, it succeeded
                    except ImportError:
                        print(
                            "Warning: Streaming mode not available, falling back to regular download"
                        )
                        download_file(
                            job.url, job.output, job.parallel, job.throttle_limit
                        )
                        success = True  # If no exception was raised, it succeeded
                else:
                    download_file(job.url, job.output, job.parallel, job.throttle_limit)
                    success = True  # If no exception was raised, it succeeded

                if success:
                    break

            except KeyboardInterrupt:
                print(f"\nJob {job.id} interrupted")
                job.status = "paused"
                return
            except Exception as e:
                print(f"Error in job {job.id}: {e}")
                job.error_message = str(e)
                if attempt == max_retries - 1:
                    break
                time.sleep(2**attempt)  # Exponential backoff

        # Update job status
        if success:
            job.status = "completed"
            job.completed_time = datetime.now().isoformat()
            job.progress = 100.0
            print(f"✅ Job {job.id} completed successfully")
        else:
            job.status = "failed"
            print(f"❌ Job {job.id} failed after {max_retries} attempts")
            if job.error_message:
                print(f"Error: {job.error_message}")

        self._save_queue()
        print()

    def stop_queue(self):
        """Stop the download queue."""
        if not self.is_running:
            print("Queue is not running")
            return

        print("Stopping queue after current download...")
        self.should_stop = True

    def get_status(self):
        """Get current queue status."""
        pending = len([j for j in self.jobs if j.status == "pending"])
        downloading = len([j for j in self.jobs if j.status == "downloading"])
        completed = len([j for j in self.jobs if j.status == "completed"])
        failed = len([j for j in self.jobs if j.status == "failed"])
        paused = len([j for j in self.jobs if j.status == "paused"])

        print("Queue Status:")
        print(f"  Total jobs: {len(self.jobs)}")
        print(f"  Pending: {pending}")
        print(f"  Downloading: {downloading}")
        print(f"  Completed: {completed}")
        print(f"  Failed: {failed}")
        print(f"  Paused: {paused}")
        print(f"  Running: {'Yes' if self.is_running else 'No'}")

        if self.current_job:
            print(f"  Current job: {self.current_job.id}")


# Global queue manager instance
_queue_manager = None


def get_queue_manager() -> QueueManager:
    """Get or create global queue manager instance."""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager


# CLI helper functions
def queue_add(
    url: str,
    output: Optional[str] = None,
    parallel: int = 4,
    streaming: bool = False,
    buffer_seconds: int = 30,
    throttle_limit: Optional[str] = None,
):
    """Add job to queue (CLI interface)."""
    manager = get_queue_manager()
    return manager.add_job(
        url, output, parallel, streaming, buffer_seconds, throttle_limit
    )


def queue_start(max_retries: int = 3):
    """Start queue processing (CLI interface)."""
    manager = get_queue_manager()
    manager.start_queue(max_retries)


def queue_stop():
    """Stop queue processing (CLI interface)."""
    manager = get_queue_manager()
    manager.stop_queue()


def queue_list():
    """List all jobs in queue (CLI interface)."""
    manager = get_queue_manager()
    manager.list_jobs()


def queue_remove(job_id: str):
    """Remove job from queue (CLI interface)."""
    manager = get_queue_manager()
    manager.remove_job(job_id)


def queue_clear(completed_only: bool = False):
    """Clear queue (CLI interface)."""
    manager = get_queue_manager()
    if completed_only:
        manager.clear_completed()
    else:
        manager.clear_all()


def queue_status():
    """Show queue status (CLI interface)."""
    manager = get_queue_manager()
    manager.get_status()
