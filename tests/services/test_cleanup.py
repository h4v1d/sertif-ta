"""Tests for PDFCleanupService."""
import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from app.services.cleanup import PDFCleanupService


class TestPDFCleanupService:
    """Test suite for PDFCleanupService."""

    @pytest.fixture
    def temp_pdf_dir(self):
        """Create a temporary directory for test PDFs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def cleanup_service(self, temp_pdf_dir):
        """Create a cleanup service instance with temp directory."""
        return PDFCleanupService(pdf_dir=temp_pdf_dir, expiry_minutes=15)

    def test_cleanup_removes_old_files(self, temp_pdf_dir, cleanup_service):
        """Test that cleanup removes files older than expiry_minutes."""
        pdf_dir = Path(temp_pdf_dir)

        # Create an old PDF file (manipulate mtime to be old)
        old_file = pdf_dir / "old_letter.pdf"
        old_file.write_text("old content")

        # Set file modification time to 20 minutes ago
        twenty_min_ago = time.time() - (20 * 60)
        import os
        os.utime(old_file, (twenty_min_ago, twenty_min_ago))

        # Create a recent PDF file
        recent_file = pdf_dir / "recent_letter.pdf"
        recent_file.write_text("recent content")

        # Run cleanup
        removed_count = cleanup_service.cleanup_old_pdfs()

        # Assertions
        assert removed_count == 1
        assert not old_file.exists()
        assert recent_file.exists()

    def test_cleanup_keeps_recent_files(self, temp_pdf_dir, cleanup_service):
        """Test that cleanup keeps files newer than expiry_minutes."""
        pdf_dir = Path(temp_pdf_dir)

        # Create two recent PDF files
        recent_file1 = pdf_dir / "recent_letter1.pdf"
        recent_file1.write_text("recent content 1")

        recent_file2 = pdf_dir / "recent_letter2.pdf"
        recent_file2.write_text("recent content 2")

        # Run cleanup
        removed_count = cleanup_service.cleanup_old_pdfs()

        # Assertions - no files should be removed
        assert removed_count == 0
        assert recent_file1.exists()
        assert recent_file2.exists()

    def test_cleanup_with_nonexistent_directory(self):
        """Test cleanup when PDF directory does not exist."""
        service = PDFCleanupService(pdf_dir="/nonexistent/path/to/pdfs")
        removed_count = service.cleanup_old_pdfs()

        # Should return 0 and not raise error
        assert removed_count == 0

    def test_cleanup_removes_multiple_old_files(self, temp_pdf_dir, cleanup_service):
        """Test cleanup removes multiple old files."""
        pdf_dir = Path(temp_pdf_dir)

        # Create multiple old PDF files
        old_files = []
        for i in range(3):
            old_file = pdf_dir / f"old_letter_{i}.pdf"
            old_file.write_text(f"old content {i}")

            # Set file modification time to 20 minutes ago
            twenty_min_ago = time.time() - (20 * 60)
            import os
            os.utime(old_file, (twenty_min_ago, twenty_min_ago))
            old_files.append(old_file)

        # Create one recent file
        recent_file = pdf_dir / "recent_letter.pdf"
        recent_file.write_text("recent content")

        # Run cleanup
        removed_count = cleanup_service.cleanup_old_pdfs()

        # Assertions
        assert removed_count == 3
        assert not any(f.exists() for f in old_files)
        assert recent_file.exists()

    def test_cleanup_with_only_non_pdf_files(self, temp_pdf_dir, cleanup_service):
        """Test cleanup ignores non-PDF files."""
        pdf_dir = Path(temp_pdf_dir)

        # Create non-PDF files
        txt_file = pdf_dir / "readme.txt"
        txt_file.write_text("readme content")

        html_file = pdf_dir / "template.html"
        html_file.write_text("<html></html>")

        # Run cleanup
        removed_count = cleanup_service.cleanup_old_pdfs()

        # Non-PDF files should not be affected
        assert removed_count == 0
        assert txt_file.exists()
        assert html_file.exists()

    def test_cleanup_with_mixed_files(self, temp_pdf_dir, cleanup_service):
        """Test cleanup only removes PDF files."""
        pdf_dir = Path(temp_pdf_dir)

        # Create old PDF
        old_pdf = pdf_dir / "old.pdf"
        old_pdf.write_text("pdf content")
        twenty_min_ago = time.time() - (20 * 60)
        import os
        os.utime(old_pdf, (twenty_min_ago, twenty_min_ago))

        # Create old non-PDF file
        old_txt = pdf_dir / "old.txt"
        old_txt.write_text("txt content")
        os.utime(old_txt, (twenty_min_ago, twenty_min_ago))

        # Run cleanup
        removed_count = cleanup_service.cleanup_old_pdfs()

        # Only PDF should be removed
        assert removed_count == 1
        assert not old_pdf.exists()
        assert old_txt.exists()

    @pytest.mark.asyncio
    async def test_start_and_stop_cleanup_task(self, cleanup_service):
        """Test starting and stopping the cleanup task."""
        # Start the cleanup task with short interval
        task = cleanup_service.start_cleanup_task(interval_seconds=1)

        # Task should be running
        assert cleanup_service.is_running
        assert not task.done()

        # Stop the task
        await cleanup_service.stop()

        # Task should be stopped
        assert not cleanup_service.is_running

    @pytest.mark.asyncio
    async def test_cleanup_task_runs_periodically(self, temp_pdf_dir):
        """Test that cleanup task runs periodically."""
        cleanup_service = PDFCleanupService(
            pdf_dir=temp_pdf_dir,
            expiry_minutes=0  # Immediate expiry for testing
        )

        # Create a PDF file
        pdf_dir = Path(temp_pdf_dir)
        test_file = pdf_dir / "test.pdf"
        test_file.write_text("content")

        # Start cleanup with very short interval
        cleanup_service.start_cleanup_task(interval_seconds=0.1)

        # Wait a bit for cleanup to run
        await asyncio.sleep(0.3)

        # File should be removed by background task
        assert not test_file.exists()

        # Stop the task
        await cleanup_service.stop()

    def test_service_initialization_defaults(self):
        """Test service initialization with default values."""
        service = PDFCleanupService()

        assert service.pdf_dir == Path("/tmp/pdfs")
        assert service.expiry_minutes == 15
        assert not service.is_running

    def test_service_initialization_custom_values(self, temp_pdf_dir):
        """Test service initialization with custom values."""
        service = PDFCleanupService(
            pdf_dir=temp_pdf_dir,
            expiry_minutes=30
        )

        assert service.pdf_dir == Path(temp_pdf_dir)
        assert service.expiry_minutes == 30

    @pytest.mark.asyncio
    async def test_multiple_start_calls(self, cleanup_service):
        """Test that multiple start calls don't create multiple tasks."""
        task1 = cleanup_service.start_cleanup_task(interval_seconds=10)
        task2 = cleanup_service.start_cleanup_task(interval_seconds=10)

        # Should return the same task
        assert task1 is task2

        # Cleanup
        await cleanup_service.stop()

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self, cleanup_service):
        """Test stopping when task is not running."""
        # Should not raise error
        await cleanup_service.stop()
        assert not cleanup_service.is_running
