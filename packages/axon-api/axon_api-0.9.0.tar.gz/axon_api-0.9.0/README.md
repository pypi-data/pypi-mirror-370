# Axon API

Zero-dependency WSGI framework with request batching, multipart streaming, and HTTP range support. Built for applications that require high performance without the bloat.

## Features

- **Zero Dependencies** - Pure Python standard library implementation
- **Multipart Streaming** - Stream multiple files in a single response with boundary separation
- **HTTP Range Support** - Partial content delivery for efficient media streaming
- **Request Sanitization** - Built-in security through input validation and sanitization
- **Structured Logging** - Thread-safe JSON logging with contextual metadata
- **WSGI Compliant** - Works with any WSGI server (Gunicorn, uWSGI, Waitress)

## Installation

```bash
pip install axon-api
```

## Quick Start

### Project Structure

```
your_project/
├── main.py              # WSGI application entry point
├── routes.py            # Route definitions
├── dev_server.py        # Development server
└── axon_api/            # Framework package
    ├── core/
    └── services/
```

### Basic Setup

```python
# main.py
from axon_api.core.application import ApplicationEngine
from routes import my_routes


def application(environ, start_response):
    """WSGI application entry point."""
    return ApplicationEngine(environ, start_response, router=my_routes)
```

```python
# routes.py
import json
from urllib.parse import parse_qsl


def my_routes(environ, request_handler):
    # Setup request context
    method = environ['method']
    path = [part for part in request_handler.path.split('/') if part]
    # Log Route
    request_handler.logger.info(f"Route: {method}, {path}")
    # Handle response
    response = request_handler.response

    match (method, path):

        case ('GET', ['hello-world']):
            # Return HTML
            return response.file("examples/hello-world.html")

        case ('GET', ['multipart', 'stream']):
            # Stream files
            files = [
                'examples/files/file1.txt',
                'examples/files/file2.txt',
                'examples/files/file3.txt'
            ]
            return response.stream(files)

        case ('GET', ['api', 'query']):
            raw_query_string = environ['query_string']
            return response.json({"raw_query_string": raw_query_string})

        case ('POST', ['api', 'json']):
            try:
                body_bytes = environ['wsgi_input'].read(environ['content_length'])
                raw_json_body = body_bytes.decode('utf-8')
                raw_parsed_data = json.loads(raw_json_body)
            except (IOError, UnicodeDecodeError, json.JSONDecodeError):
                raise
            return response.json({"raw_parsed_data": raw_parsed_data})

        case ('GET', ['api', 'health']):
            # Return JSON
            return response.json({"status": "available"})

        case _:
            # Return message
            return response.message("Not Found", status_code=404)
```

```python
# dev_server.py
from main import application

if __name__ == "__main__":
    try:
        from wsgiref.simple_server import make_server

        httpd = make_server('', 9000, application)
        print('Starting server..')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Exiting server..')
```

### Running the Application

```bash
# Development (using included server)
python dev_server.py
# Server runs on http://localhost:9000

# Production with Gunicorn
gunicorn -w 4 main:application

# Production with uWSGI
uwsgi --http :8000 --wsgi-file main.py --callable application
```

## Core Components

### ApplicationEngine

Central request processor with automatic error handling:

```python
def application(environ, start_response):
    """WSGI application entry point."""
    return ApplicationEngine(environ, start_response, router=my_routes)
```

### Response Methods

The response object provides multiple content delivery methods:

```python
def my_routes(environ, request_handler):
    # Setup request context
    method = environ['method']
    path = [part for part in request_handler.path.split('/') if part]
    # Log Route
    request_handler.logger.info(f"Route: {method}, {path}")
    # Handle response
    response = request_handler.response
    
    match (method, path):
        
        case ('GET', ['hello-world']):
            # Return HTML
            return response.file("examples/hello-world.html")

        case ('GET', ['api', 'health']):
            # Return JSON
            return response.json({"status": "available"})

        case _:
            # Return message
            return response.message("Not Found", status_code=404)
```

### Multipart Streaming

Stream multiple files in a single HTTP response:

```python
case ('GET', ['multipart', 'stream']):
    # Stream files
    files = [
        'examples/app.js',
        'examples/style.css',
        'examples/logo.png'
    ]
    return response.stream(files)
```

Browser receives multipart response with boundaries:

```
--boundary_abc123
Content-Type: text/javascript
Content-Length: 1024
Content-Disposition: inline; filename="app.js"

[file content]
--boundary_abc123
Content-Type: text/css
Content-Length: 512
Content-Disposition: inline; filename="styles.css"

[file content]
--boundary_abc123--
```

### Dynamic File Streaming

Dynamic file selection and streaming via query parameters:

```python
case ('GET', ['api', 'stream-files']):
    # Return batched response for batched request
    raw_query_string = environ['query_string']

    if not raw_query_string:
        return response.message("No files specified in query parameters", status_code=400)

    # Parse query parameters to get file paths
    query_params = dict(parse_qsl(raw_query_string))

    # Extract all file paths from query parameters
    files = list(query_params.values())

    if not files:
        return response.message("No valid file parameters found", status_code=400)

    # Stream the requested files
    return response.stream(files)
```

### Request Sanitization

All requests are automatically sanitized with configurable limits:

```python
# Sanitizer enforces:
# - Max path length: 2048 chars
# - Max header length: 8192 chars  
# - Max content length: 10MB
# - Allowed methods: GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH
# - Control character removal
# - Input stream wrapping with size limits
```

### Error Handling

Centralized error mapping with automatic logging:

```python
# Automatic error responses:
# FileNotFoundError → 404 Not Found
# PermissionError → 403 Forbidden
# SecurityError → 400 Bad Request
# ValueError (method) → 405 Method Not Allowed
# Exception → 500 Internal Server Error
```

## Advanced Usage

### Pattern Matching Routes

Leverage Python 3.10+ pattern matching:

```python
def my_routes(environ, request_handler):
    # Setup request context
    method = environ['method']
    path = [part for part in request_handler.path.split('/') if part]
    # Log Route
    request_handler.logger.info(f"Route: {method}, {path}")
    # Handle response
    response = request_handler.response

    match (method, path):

        case ('GET', ['hello-world']):
            # Return HTML
            return response.file("examples/hello-world.html")
            
        case ('GET', ['static', *filepath]):
            file_path = '/'.join(filepath)
            return response.file(f"static/{file_path}")

        case ('GET', ['api', 'health']):
            # Return JSON
            return response.json({"status": "available"})

        case _:
            # Return message
            return response.message("Not Found", status_code=404)
```

### Processing Request Data

```python
    # JSON body
    import json
    body = environ['wsgi_input'].read(environ['content_length'])
    data = json.loads(body.decode('utf-8'))
```
```python
    # Form data
    from urllib.parse import parse_qsl
    form_data = parse_qsl(body.decode('utf-8'))
```
```python
    # Query parameters
    from urllib.parse import parse_qsl
    params = dict(parse_qsl(environ['query_string']))
```

### Structured Logging

Thread-safe logging with JSON metadata:

```python
request_handler.logger.info("Request processed", 
    status_code=200, 
    path="/api/users",
    user_id=123,
    response_time=0.045
)

# Output: [2024-01-15 10:30:45] [INFO] Request processed | {"status_code":200,"path":"/api/users","user_id":123,"response_time":0.045}
```

## Architecture

```
axon_api/
├── core/
│   ├── application.py   # WSGI application engine
│   ├── response.py      # Response handling
│   ├── sanitizer.py     # Input validation and sanitization
│   ├── streaming.py     # File streaming with range support
│   ├── headers.py       # HTTP header utilities
│   ├── mimetype.py      # MIME type detection
│   └── errors.py        # Error handling and mapping
└── services/
    └── logger.py        # Thread-safe structured logging
```

## Production Deployment

### Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --worker-class sync \
  app:application
```

### uWSGI

```ini
[uwsgi]
module = app:application
master = true
processes = 4
socket = /tmp/axon.sock
chmod-socket = 666
vacuum = true
die-on-term = true
```

### Nginx Configuration

```nginx
upstream axon_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name example.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://axon_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # Let Nginx handle static files directly
    location /static/ {
        alias /path/to/static/;
        expires 30d;
    }
}
```

## Performance Considerations

### Multipart Streaming Benefits

Traditional approach (10 separate requests):
```
Browser → 10 HTTP requests → Server → 10 responses
```

Axon multipart streaming (1 batched request):
```
Browser → 1 HTTP request → Server → 1 multipart response
```

Result: 90% reduction in HTTP overhead, lower latency, better connection utilization.

### Memory Efficiency

- Streaming uses generators with 64KB chunks
- No full file loading into memory
- Efficient for large file transfers
- LimitedReader enforces content-length limits

## Security Features

- **Input Sanitization**: Automatic removal of control characters
- **Size Limits**: Configurable limits for paths, headers, and content
- **Method Validation**: Only allowed HTTP methods accepted
- **Content Length Enforcement**: Prevents resource exhaustion
- **Error Masking**: Generic error messages prevent information leakage

## Limitations

- No built-in authentication/authorization
- No built-in body sanitization
- No session management
- No template engine
- No ORM/database integration
- WSGI only (no ASGI/async support)

## Requirements

- Python 3.10+ (uses structural pattern matching)
- No external dependencies

## Contributing

Contributions must:
- Maintain zero-dependency philosophy
- Use only Python standard library
- Include tests for new features
- Follow existing code patterns
- Pass security review

## License

MIT License

## Support

- Security: Report vulnerabilities to b-is-for-build@bellone.com