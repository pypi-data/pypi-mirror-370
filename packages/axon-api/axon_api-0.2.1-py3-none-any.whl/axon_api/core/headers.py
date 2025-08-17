"""
HTTP header utilities and status code mapping.

Provides header construction and comprehensive HTTP status code to string conversion
for WSGI response building.
"""
from typing import Union, List, Tuple


def build_http_headers(mimetype: str, include_cors: bool = False) -> List[Tuple[str, str]]:
    """Build HTTP headers list with content-type and optional CORS headers."""
    headers = [
        ('Content-Type', mimetype)
    ]

    # Add CORS headers only when explicitly requested
    if include_cors:
        headers.extend([
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ])

    # Add specific headers based on content type
    if mimetype == 'multipart/byteranges':
        # Enable range request support for multipart responses
        headers.append(('Accept-Ranges', 'bytes'))

    return headers


def get_http_status(status_code: Union[int, str, None]) -> str:
    """Convert status code to full HTTP status string (e.g., 200 -> "200 OK")."""
    # Handle None case - default to server error
    if status_code is None:
        return "500 Internal Server Error"
    try:
        code = int(status_code)
        http_codes = {
            # 1xx Informational
            100: "100 Continue",
            101: "101 Switching Protocols",
            102: "102 Processing",
            103: "103 Early Hints",
            # 2xx Success
            200: "200 OK",
            201: "201 Created",
            202: "202 Accepted",
            203: "203 Non-Authoritative Information",
            204: "204 No Content",
            205: "205 Reset Content",
            206: "206 Partial Content",
            207: "207 Multi-Status",
            208: "208 Already Reported",
            226: "226 IM Used",
            # 3xx Redirection
            300: "300 Multiple Choices",
            301: "301 Moved Permanently",
            302: "302 Found",
            303: "303 See Other",
            304: "304 Not Modified",
            305: "305 Use Proxy",
            307: "307 Temporary Redirect",
            308: "308 Permanent Redirect",
            # 4xx Client Error
            400: "400 Bad Request",
            401: "401 Unauthorized",
            402: "402 Payment Required",
            403: "403 Forbidden",
            404: "404 Not Found",
            405: "405 Method Not Allowed",
            406: "406 Not Acceptable",
            407: "407 Proxy Authentication Required",
            408: "408 Request Timeout",
            409: "409 Conflict",
            410: "410 Gone",
            411: "411 Length Required",
            412: "412 Precondition Failed",
            413: "413 Payload Too Large",
            414: "414 URI Too Long",
            415: "415 Unsupported Media Type",
            416: "416 Range Not Satisfiable",
            417: "417 Expectation Failed",
            418: "418 I'm a teapot",
            421: "421 Misdirected Request",
            422: "422 Unprocessable Content",
            423: "423 Locked",
            424: "424 Failed Dependency",
            425: "425 Too Early",
            426: "426 Upgrade Required",
            428: "428 Precondition Required",
            429: "429 Too Many Requests",
            431: "431 Request Header Fields Too Large",
            451: "451 Unavailable For Legal Reasons",
            # 5xx Server Error
            500: "500 Internal Server Error",
            501: "501 Not Implemented",
            502: "502 Bad Gateway",
            503: "503 Service Unavailable",
            504: "504 Gateway Timeout",
            505: "505 HTTP Version Not Supported",
            506: "506 Variant Also Negotiates",
            507: "507 Insufficient Storage",
            508: "508 Loop Detected",
            510: "510 Not Extended",
            511: "511 Network Authentication Required"
        }

        # Try dictionary lookup first
        if code in http_codes:
            return http_codes[code]

        # Handle unknown codes by range
        if 100 <= code < 200:
            return f"{code} Informational"
        elif 200 <= code < 300:
            return f"{code} Success"
        elif 300 <= code < 400:
            return f"{code} Redirection"
        elif 400 <= code < 500:
            return f"{code} Client Error"
        elif 500 <= code < 600:
            return f"{code} Server Error"
        else:
            return f"{code} Unknown Status"

    except (ValueError, TypeError) as error:
        raise ValueError(f"Invalid HTTP status code format: {status_code}") from error
