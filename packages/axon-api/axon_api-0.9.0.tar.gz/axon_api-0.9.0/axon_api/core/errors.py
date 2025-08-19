"""
Exception handling and HTTP error mapping.

Maps Python exceptions to appropriate HTTP status codes with centralized logging
and security-aware error message handling.
"""
from typing import Dict, Any


class SecurityError(Exception):
    """Raised for input validation failures and security policy violations."""
    pass


class ErrorHandler:
    """Maps exceptions to HTTP status codes and handles error logging."""
    # Static mapping for common errors
    ERROR_MAP = {
        "FileNotFoundError": (404, "Not Found", False),  # (status, message, should_log)
        "PermissionError": (403, "Forbidden", True),
        "SecurityError": (400, "Bad Request", True),
    }

    def __init__(self, logger, start_response) -> None:
        self.logger = logger
        self.start_response = start_response

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bytes:
        """Convert exception to appropriate HTTP error response with logging."""
        error_type = type(error)

        error_name = error_type.__name__
        if error_name in self.ERROR_MAP:
            status_code, message, should_log = self.ERROR_MAP[error_name]
        elif isinstance(error, ValueError) and "Invalid HTTP method" in str(error):
            status_code, message, should_log = 405, "Method Not Allowed", True
        else:
            # Unknown error
            status_code, message, should_log = 500, "Internal Server Error", True
            context = {**context, "error": str(error)}

        # Log if needed
        if should_log:
            log_method = self.logger.warning if status_code < 500 else self.logger.error
            log_method(f"{error_type.__name__}: {message}", status_code=status_code, **context)

        # Return HTTP response
        from axon_api.core.headers import get_http_status

        status = get_http_status(status_code)
        headers = [('Content-Type', 'text/plain; charset=utf-8')]

        self.start_response(status, headers)
        return message.encode('utf-8')
