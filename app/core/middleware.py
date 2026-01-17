"""Custom middleware for request validation."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core import get_logger
import re

logger = get_logger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating requests."""

    # Allowed filename pattern: alphanumeric, underscores, hyphens, dots
    ALLOWED_FILENAME_PATTERN = re.compile(r'^[\w\-. ]+$')

    # Blocked patterns for path traversal
    BLOCKED_PATTERNS = ['..', '\\', '~/', '/etc/', '/var/']

    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        # Log request
        logger.info(f"{request.method} {request.url.path}")

        # Validate path parameters for downloads
        if request.url.path.startswith("/api/v1/letters/download/"):
            filename = request.path_params.get("filename", "")
            if not self._is_valid_filename(filename):
                logger.warning(f"Invalid filename detected: {filename}")
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=400,
                    content={"error": {"code": "INVALID_FILENAME", "message": "Invalid filename"}}
                )

        response = await call_next(request)
        return response

    def _is_valid_filename(self, filename: str) -> bool:
        """Check if filename is valid and safe."""
        if not filename:
            return False

        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in filename:
                return False

        # Check against allowed pattern
        if not self.ALLOWED_FILENAME_PATTERN.match(filename):
            return False

        return True
