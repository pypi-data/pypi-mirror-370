"""
MIME type detection for file extensions.

Maps file extensions to appropriate MIME types for HTTP Content-Type headers
with fallback to application/octet-stream.
"""
from typing import Optional


def get_mimetype(file_extension: Optional[str]) -> str:
    """Return MIME type for file extension. Defaults to application/octet-stream."""
    if not file_extension:
        return 'application/octet-stream'

    extension = file_extension.lstrip('.').lower()

    mimetypes = {
        # Audio formats
        "aac": 'audio/aac',
        "cda": 'application/x-cdf',
        "mid": 'audio/midi',
        "midi": 'audio/x-midi',
        "mp3": 'audio/mpeg',
        "oga": 'audio/ogg',
        "ogg": 'audio/ogg',
        "wav": 'audio/wav',
        "weba": 'audio/webm',

        # Font formats
        "eot": 'application/vnd.ms-fontobject',
        "otf": 'font/otf',
        "ttf": 'font/ttf',
        "woff": 'font/woff',
        "woff2": 'font/woff2',

        # Image formats
        "apng": 'image/apng',
        "avif": 'image/avif',
        "gif": 'image/gif',
        "ico": 'image/x-icon',
        "jpeg": 'image/jpeg',
        "jpg": 'image/jpeg',
        "png": 'image/png',
        "svg": 'image/svg+xml',
        "webp": 'image/webp',

        # Text and web formats
        "css": 'text/css; charset=utf-8',
        "html": 'text/html; charset=utf-8',
        "htm": 'text/html; charset=utf-8',
        "js": 'text/javascript; charset=utf-8',
        "json": 'application/json; charset=utf-8',
        "xml": 'application/xml; charset=utf-8',
        "csv": 'text/csv; charset=utf-8',
        "txt": 'text/plain; charset=utf-8',
        "manifest": 'application/manifest+json',

        # Video formats
        "avi": 'video/x-msvideo',
        "mp4": 'video/mp4',
        "mpeg": 'video/mpeg',
        "ogv": 'video/ogg',
        "ts": 'video/mp2t',
        "webm": 'video/webm',

        # Document formats
        "pdf": 'application/pdf',
        "doc": 'application/msword',
        "docx": 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        "xls": 'application/vnd.ms-excel',
        "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        "ppt": 'application/vnd.ms-powerpoint',
        "pptx": 'application/vnd.openxmlformats-officedocument.presentationml.presentation',

        # Archive formats
        "zip": 'application/zip',
        "tar": 'application/x-tar',
        "gz": 'application/gzip',
        "7z": 'application/x-7z-compressed',
        "rar": 'application/vnd.rar',

        # Web Assembly
        "wasm": 'application/wasm',

        # Special streaming case
        "stream": 'multipart/byteranges'
    }

    return mimetypes.get(extension, 'application/octet-stream')
