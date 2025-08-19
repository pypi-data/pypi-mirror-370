"""
WSGI request sanitization and security validation.

Enforces security limits on request components (paths, headers, content) and provides
input stream wrapping to prevent resource exhaustion attacks.
"""
from typing import Dict, Any, Optional, Set
import re

from axon_api.core.errors import SecurityError


class LimitedReader:
    """Input stream wrapper that enforces content-length limits to prevent memory exhaustion."""

    def __init__(self, stream, content_length):
        self.stream = stream
        self.remaining = content_length

    def read(self, size=-1):
        if self.remaining <= 0:
            return b''
        to_read = min(size, self.remaining) if size > 0 else self.remaining
        data = self.stream.read(to_read)
        self.remaining -= len(data)
        return data


def _wrap_input_stream(stream, content_length):
    return LimitedReader(stream, content_length)


def sanitize_environ(environ: Dict[str, Any],
                     max_path_length: int = 2048,
                     max_header_length: int = 8192,
                     max_query_length: int = 2048,
                     max_content_length: int = 10 * 1024 * 1024,  # 10MB
                     allowed_methods: Optional[Set[str]] = None) -> Dict[str, Any]:
    """Sanitize and validate WSGI environ. Returns cleaned dict with security limits enforced."""
    allowed_methods = allowed_methods or {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'}

    try:
        # Validate required WSGI variables exist
        _validate_wsgi_requirements(environ)

        env = {
            'method': _sanitize_method(environ.get('REQUEST_METHOD', ''), allowed_methods),
            'path_info': _sanitize_path(environ.get('PATH_INFO', '/'), max_path_length),
            'query_string': _sanitize_query(environ.get('QUERY_STRING', ''), max_query_length),
            # Raw content type required for multipart/file uploads
            'content_type': _sanitize_content_type(environ.get('CONTENT_TYPE')),
            'content_length': _sanitize_content_length(environ.get('CONTENT_LENGTH', '0'), max_content_length),
            'remote_addr': _sanitize_ip(environ.get('REMOTE_ADDR', '')),
            'headers': _sanitize_headers(environ, max_header_length),
            'server_name': _sanitize_server_name(environ.get('SERVER_NAME', 'localhost')),
            'server_port': _sanitize_server_port(environ.get('SERVER_PORT', '80')),
            'wsgi_version': environ['wsgi.version'],
            'wsgi_url_scheme': environ['wsgi.url_scheme'],
            'wsgi_errors': environ['wsgi.errors']
        }

        sanitized_wsgi_input = LimitedReader(environ['wsgi.input'], env['content_length'])
        env.update({'wsgi_input': sanitized_wsgi_input})
        return env
    except ValueError as e:
        raise SecurityError(str(e))


# Compile pattern once at module level for performance
_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x1F\x7F]')


def _sanitize_method(method: str, allowed_methods: Set[str]) -> str:
    """Validate and sanitize HTTP method."""
    method = method.upper()
    if method not in allowed_methods:
        raise ValueError(f"Invalid HTTP method: {method}")
    return method


def _sanitize_path(path: str, max_length: int) -> str:
    """Sanitize and validate request path."""
    if len(path) > max_length:
        raise ValueError("Path too long")

    # Remove control characters
    path = _CONTROL_CHAR_PATTERN.sub('', path)

    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path

    return path


def _sanitize_query(query: str, max_length: int) -> str:
    """Sanitize query string."""
    if len(query) > max_length:
        raise ValueError("Query string too long")
    return _CONTROL_CHAR_PATTERN.sub('', query)


def _sanitize_content_type(content_type: Optional[str]) -> Optional[str]:
    """Sanitize content type header."""
    if content_type is None:
        return None

    # Basic content type validation
    content_type = content_type.lower()
    if len(content_type) > 100 or ';' in content_type:
        # If complex content type, only keep the main type
        content_type = content_type.split(';')[0].strip()

    return content_type


def _sanitize_content_length(length: str, max_length: int) -> int:
    """Sanitize and validate content length."""
    try:
        length_int = int(length)
        if length_int < 0:
            return 0
        if length_int > max_length:
            raise ValueError(f"Content too large: {length_int} bytes exceeds {max_length}")
        return length_int
    except ValueError as e:
        if "Content too large" in str(e):
            raise  # Re-raise the size error
        return 0  # Invalid format defaults to 0


def _sanitize_headers(environ: Dict[str, Any], max_header_length: int) -> Dict[str, str]:
    """Extract and sanitize HTTP headers from environ."""
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].lower().replace('_', '-')
            if len(str(value)) > max_header_length:
                raise ValueError(f"Header too long: {header_name}")
            headers[header_name] = str(value)
    return headers


def _sanitize_ip(ip: str) -> str:
    """Sanitize IP address."""
    if len(ip) > 39:  # Max length of IPv6
        return ''
    return ip.split(',')[0].strip()  # Handle X-Forwarded-For header


def _sanitize_server_name(name: str) -> str:
    """Sanitize server name."""
    return _CONTROL_CHAR_PATTERN.sub('', name)[:253]


def _sanitize_server_port(port: str) -> int:
    """Sanitize server port."""
    try:
        return int(port)
    except ValueError:
        return 80


def _validate_wsgi_requirements(environ: Dict[str, Any]) -> None:
    """Validate that required WSGI variables are present."""
    required = {'wsgi.version', 'wsgi.url_scheme', 'wsgi.input', 'wsgi.errors'}
    missing = required - set(environ.keys())
    if missing:
        raise ValueError(f"Missing required WSGI variables: {missing}")
