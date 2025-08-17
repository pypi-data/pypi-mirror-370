"""
HTTP response builder with streaming and multipart support.

Provides methods for JSON, file, redirect, and streaming responses with automatic
MIME type detection and HTTP range request handling.
"""
from typing import Optional, List, Iterator, Union, Dict, Callable

from axon_api.core.headers import build_http_headers, get_http_status
from axon_api.core.mimetype import get_mimetype
from axon_api.core.streaming import stream_single_file, stream_multipart_files


class Response:
    """HTTP response builder with support for files, JSON, streaming, and redirects."""

    def __init__(self, start_response: Callable, logger) -> None:
        self.start_response = start_response
        self.logger = logger

    def file(self, file_path: str, status_code: int = 200, mimetype: Optional[str] = None) -> bytes:
        """Return file content with auto-detected or specified MIME type."""
        # Auto-detect mimetype from extension
        if mimetype is None:
            extension = file_path.split('.')[-1] if '.' in file_path else ''
            mimetype = get_mimetype(extension)

        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()

        # Build response
        status = get_http_status(status_code)
        headers = build_http_headers(mimetype)

        self.logger.info(f"File response: {file_path}", status_code=status_code, size=len(content))
        self.start_response(status, headers)
        return content

    def message(self, content: str, status_code: int = 200, mimetype: str = 'text/plain') -> bytes:
        """Return plain text or custom content type response."""
        data = content.encode('utf-8')
        status = get_http_status(status_code)
        headers = build_http_headers(mimetype)

        self.logger.info(f"Message response", status_code=status_code, size=len(data))
        self.start_response(status, headers)
        return data

    def stream(self,
              files: Union[str, List[str]],
              status_code: int = 200,
              range_header: Optional[str] = None) -> Iterator[bytes]:
        """Stream single file (with range support) or multiple files as multipart response."""
        # Normalize input
        if isinstance(files, str):
            files = [files]

        # Single file with optional range support
        if len(files) == 1:
            file_path = files[0]
            result = stream_single_file(file_path, range_header)

            # Build headers
            extension = file_path.split('.')[-1] if '.' in file_path else ''
            mimetype = get_mimetype(extension)
            headers = build_http_headers(mimetype)

            # Handle range requests
            if result['is_range']:
                status_code = 206
                headers.extend([
                    ('Accept-Ranges', 'bytes'),
                    ('Content-Range', f"bytes {result['start']}-{result['end']}/{result['file_size']}"),
                    ('Content-Length', str(result['end'] - result['start'] + 1))
                ])
            else:
                headers.append(('Content-Length', str(result['file_size'])))

            status = get_http_status(status_code)
            self.logger.info(f"Streaming file: {file_path}", status_code=status_code)
            self.start_response(status, headers)
            return result['generator']

        # Multiple files - multipart response
        else:
            result = stream_multipart_files(files)
            mimetype = f"multipart/byteranges; boundary={result['boundary']}"
            headers = build_http_headers(mimetype)

            status = get_http_status(status_code)
            self.logger.info(f"Streaming multipart: {len(files)} files", status_code=status_code)
            self.start_response(status, headers)
            return result['generator']

    def json(self, data: Union[str, Dict, List], status_code: int = 200) -> bytes:
        """Return JSON response with proper content-type header."""
        import json as json_module

        if isinstance(data, str):
            content = data
        else:
            content = json_module.dumps(data)

        return self.message(content, status_code, 'application/json; charset=utf-8')

    def redirect(self, location: str, status_code: int = 302) -> bytes:
        """Return HTTP redirect response."""
        status = get_http_status(status_code)
        headers = [('Location', location), ('Content-Type', 'text/plain')]

        self.logger.info(f"Redirect to: {location}", status_code=status_code)
        self.start_response(status, headers)
        return b''
