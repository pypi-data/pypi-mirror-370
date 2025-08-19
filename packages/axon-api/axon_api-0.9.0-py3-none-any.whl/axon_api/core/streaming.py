"""
File streaming with HTTP range and multipart support.

Handles single file streaming with range requests and multipart responses for
efficient delivery of multiple files in a single HTTP response.
"""
import os
import uuid
from typing import Dict, Any, List, Iterator, Tuple, Optional
from axon_api.core.mimetype import get_mimetype


def stream_single_file(file_path: str, range_header: Optional[str] = None) -> Dict[str, Any]:
    """Stream single file with optional HTTP range support. Returns generator and metadata."""
    file_size = get_file_size(file_path)
    start, end = parse_range_header(range_header, file_size)

    return {
        'generator': stream_file_range(file_path, start, end),
        'file_size': file_size,
        'start': start,
        'end': end,
        'is_range': bool(range_header)
    }


def stream_multipart_files(requested_files: List[str],
                           boundary: Optional[str] = None) -> Dict[str, Any]:
    """Stream multiple files as multipart/byteranges response with auto-generated boundary."""
    # Generate unique boundary if not provided
    boundary = boundary or f"boundary_{uuid.uuid4().hex[:16]}"

    def generate() -> Iterator[bytes]:
        """Generate multipart content with proper boundaries and headers."""
        for file_path in requested_files:
            # Extract file name from path
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path

            # Get file metadata
            file_size = get_file_size(file_path)

            # Extensionless files default to 'application/octet-stream'
            extension = file_path.split('.')[-1] if '.' in file_path else ''
            file_mimetype = get_mimetype(extension) or 'application/octet-stream'

            # Yield multipart section header
            part_header = (
                f"\r\n--{boundary}\r\n"
                f"Content-Type: {file_mimetype}\r\n"
                f"Content-Length: {file_size}\r\n"
                f"Content-Disposition: inline; filename=\"{file_name}\"\r\n"
                f"\r\n"
            ).encode('utf-8')
            yield part_header

            # Yield file content in chunks
            yield from stream_file_range(file_path, 0, file_size - 1)

        # Yield final boundary to close multipart response
        yield f"\r\n--{boundary}--\r\n".encode('utf-8')

    return {
        'generator': generate(),
        'boundary': boundary
    }


def parse_range_header(range_header: Optional[str], file_size: int) -> Tuple[int, int]:
    """Parse HTTP Range header into (start, end) byte positions. Returns full range if invalid."""
    # Return full file range if no range header or invalid format
    if not range_header or not range_header.startswith('bytes='):
        return 0, file_size - 1

    try:
        # Extract range specification (everything after "bytes=")
        range_spec = range_header[6:]
        if '-' not in range_spec:
            return 0, file_size - 1

        # Split into start and end components
        start_str, end_str = range_spec.split('-', 1)

        # Handle different range formats
        if start_str and end_str:
            # Format: "start-end"
            start = int(start_str)
            end = int(end_str)
        elif start_str and not end_str:
            # Format: "start-" (from start to end of file)
            start = int(start_str)
            end = file_size - 1
        elif not start_str and end_str:
            # Format: "-end" (last N bytes)
            suffix_length = int(end_str)
            start = max(0, file_size - suffix_length)
            end = file_size - 1
        else:
            # Invalid format
            return 0, file_size - 1

        # Validate and clamp ranges
        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))

        return start, end

    except (ValueError, IndexError):
        # Invalid range format - return full file
        return 0, file_size - 1


def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)


def stream_file_range(file_path: str, start: int = 0, end: Optional[int] = None,
                      chunk_size: int = 65536) -> Iterator[bytes]:
    """Stream file content in chunks from start to end byte positions."""
    with open(file_path, 'rb') as file:
        # Seek to starting position
        file.seek(start)

        # Calculate remaining bytes to read
        remaining = (end - start + 1) if end is not None else float('inf')

        # Stream file in chunks
        while remaining > 0:
            # Read chunk, limited by remaining bytes and chunk size
            read_size = min(chunk_size, int(remaining)) if remaining != float('inf') else chunk_size
            chunk = file.read(read_size)

            # Break if no more data (EOF reached)
            if not chunk:
                break

            # Update remaining count and yield chunk
            if remaining != float('inf'):
                remaining -= len(chunk)

            yield chunk
