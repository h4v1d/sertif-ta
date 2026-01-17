"""Custom exception classes for the application."""


class AppException(Exception):
    """Base exception class for application errors."""

    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class PDFGenerationError(AppException):
    """Raised when PDF generation fails."""

    def __init__(self, message: str = "Failed to generate PDF"):
        super().__init__(message, code="PDF_GENERATION_ERROR")


class TemplateNotFoundError(AppException):
    """Raised when a PDF template is not found."""

    def __init__(self, template_name: str):
        super().__init__(
            f"Template '{template_name}' not found",
            code="TEMPLATE_NOT_FOUND"
        )


class InvalidRequestError(AppException):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Invalid request data"):
        super().__init__(message, code="INVALID_REQUEST")


class FileNotFoundError(AppException):
    """Raised when a requested file is not found."""

    def __init__(self, filename: str):
        super().__init__(
            f"File '{filename}' not found",
            code="FILE_NOT_FOUND"
        )
