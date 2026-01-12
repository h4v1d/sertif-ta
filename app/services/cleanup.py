"""Background cleanup service for removing old PDF files."""
import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PDFCleanupService:
    """Service for periodic cleanup of old PDF files."""

    def __init__(self, pdf_dir: str = "/tmp/pdfs", expiry_minutes: int = 15):
        """
        Initialize the cleanup service.

        Args:
            pdf_dir: Directory containing PDF files to clean up.
            expiry_minutes: Age in minutes after which PDFs should be removed.
        """
        self.pdf_dir = Path(pdf_dir)
        self.expiry_minutes = expiry_minutes
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._running = False

    def cleanup_old_pdfs(self) -> int:
        """
        Remove PDF files older than expiry_minutes.

        Returns:
            Number of files removed.
        """
        if not self.pdf_dir.exists():
            logger.debug(f"PDF directory {self.pdf_dir} does not exist, skipping cleanup")
            return 0

        import time
        current_time = time.time()
        expiry_seconds = self.expiry_minutes * 60
        removed_count = 0

        try:
            for pdf_file in self.pdf_dir.glob("*.pdf"):
                try:
                    file_mtime = pdf_file.stat().st_mtime
                    file_age = current_time - file_mtime

                    if file_age > expiry_seconds:
                        pdf_file.unlink()
                        removed_count += 1
                        logger.info(
                            f"Removed old PDF: {pdf_file.name} "
                            f"(age: {file_age / 60:.1f} minutes)"
                        )
                except (OSError, IOError) as e:
                    logger.warning(f"Failed to process {pdf_file}: {e}")
        except (OSError, IOError) as e:
            logger.error(f"Error during cleanup: {e}")

        if removed_count > 0:
            logger.info(f"Cleanup complete: removed {removed_count} old PDF(s)")
        else:
            logger.debug("Cleanup complete: no old PDFs found")

        return removed_count

    async def _cleanup_loop(self, interval_seconds: int = 300):
        """
        Internal async loop for periodic cleanup.

        Args:
            interval_seconds: Seconds between cleanup runs.
        """
        self._running = True
        logger.info(
            f"Starting cleanup task: interval={interval_seconds}s, "
            f"expiry={self.expiry_minutes}min, dir={self.pdf_dir}"
        )

        while not self._stop_event.is_set():
            try:
                # Run cleanup in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.cleanup_old_pdfs)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

            # Wait for interval or stop event
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=interval_seconds
                )
                break
            except asyncio.TimeoutError:
                # Timeout is expected, continue loop
                pass

        self._running = False
        logger.info("Cleanup task stopped")

    def start_cleanup_task(self, interval_seconds: int = 300) -> asyncio.Task:
        """
        Start the background cleanup task.

        Args:
            interval_seconds: Seconds between cleanup runs (default: 300 = 5 minutes).

        Returns:
            The asyncio Task running the cleanup loop.
        """
        if self._cleanup_task is not None and not self._cleanup_task.done():
            logger.warning("Cleanup task is already running")
            return self._cleanup_task

        self._stop_event.clear()
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval_seconds))
        return self._cleanup_task

    async def stop(self):
        """Stop the background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            logger.debug("Cleanup task is not running")
            return

        logger.info("Stopping cleanup task...")
        self._stop_event.set()

        try:
            await asyncio.wait_for(self._cleanup_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Cleanup task did not stop gracefully, cancelling")
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._running = False
        logger.info("Cleanup task stopped")

    @property
    def is_running(self) -> bool:
        """Check if the cleanup task is currently running."""
        return self._running and self._cleanup_task is not None and not self._cleanup_task.done()
