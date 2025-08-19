"""
WSGI application engine with request sanitization and error handling.

Central request processor that coordinates sanitization, routing, and response generation
with automatic error mapping and structured logging.
"""
from typing import Iterator, Callable

from axon_api.core.errors import ErrorHandler
from axon_api.core.sanitizer import sanitize_environ
from axon_api.services.logger import get_logger
from axon_api.core.response import Response


class ApplicationEngine:
    """WSGI application engine that handles request sanitization, routing, and error handling."""

    def __init__(self, environ: dict, start_response: callable, router: Callable = None) -> None:
        self.start_response = start_response
        self.environ = sanitize_environ(environ)
        self.logger = get_logger('logs')
        self.error_handler = ErrorHandler(self.logger, start_response)
        self.path = self.environ['path_info']
        self.response = Response(self.start_response, self.logger)
        self.router = router

    def __iter__(self) -> Iterator[bytes]:
        """Process request through router and yield response content as bytes."""
        if not self.router:
            raise ValueError("No router function provided")

        try:
            response_content = self.router(self.environ, self)

            # All responses must be iterables of bytes
            if hasattr(response_content, '__iter__') and not isinstance(response_content, (str, bytes)):
                yield from response_content
            else:
                # Convert single bytes/string to iterable
                yield response_content if isinstance(response_content, bytes) else response_content.encode('utf-8')

        except Exception as e:
            context = {
                'path': self.path,
                'method': self.environ['method']
            }
            yield self.error_handler.handle_error(e, context)

    def close(self):
        pass
