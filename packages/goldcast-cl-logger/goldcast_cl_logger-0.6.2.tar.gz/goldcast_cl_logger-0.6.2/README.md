# goldcast-cl-logger

A lightweight, flexible logging library for Content Lab projects with distributed tracing support.

## Installation

```bash
# Install from GitHub Packages (recommended)
pip install goldcast-cl-logger

# Install with HTTP extras for traced requests
pip install goldcast-cl-logger[http]

# Add to requirements.txt
goldcast-cl-logger==0.2.8

# Add to pyproject.toml (Poetry)
[[tool.poetry.source]]
name = "github"
url = "https://ghcr.io/goldcast"

[tool.poetry.dependencies]
goldcast-cl-logger = { version = "^0.2.8", source = "github" }
```

## Features

- **Simple API**: Easy to use with minimal configuration
- **JSON Logging by Default**: Structured JSON logging for better observability
- **Distributed Tracing**: Built-in support for trace ID propagation
- **Sentry Integration**: Compatible with Sentry's distributed tracing
- **Environment Configuration**: Control logging format via environment variables
- **Extra Context**: Add custom fields to log entries
- **File Logging**: Optional file output support
- **Zero Dependencies**: Uses only Python standard library (requests is optional)
- **HTTP & SQS Propagation**: Automatic trace ID propagation for external calls

## Quick Start

```python
from cl_logger import get_logger

# Get a logger instance
logger = get_logger(__name__)

# Basic logging (JSON by default)
logger.info("Application started")
logger.error("Something went wrong")

# With extra context
logger.info("User action", extra={"user_id": 123, "action": "login"})

# Exception logging with traceback
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", extra={"operation": "risky_operation"})
```

## Distributed Tracing

### Automatic Trace ID Propagation

The logger automatically includes trace IDs in all log entries when used with the provided middleware:

```python
# Django middleware automatically creates/extracts trace IDs
# In settings.py:
MIDDLEWARE = [
    # ...
    'content_lab_backend.middleware.logging_middleware.RequestLoggingMiddleware',
    # ...
]
```

### Manual Trace Context

```python
from cl_logger import TraceContext, get_trace_id

# Create a new trace context
with TraceContext() as ctx:
    logger.info("Starting operation")
    # trace_id is automatically included in logs
    current_trace_id = get_trace_id()
```

### HTTP Request Propagation

```python
from cl_logger import http_utils

# Use traced HTTP client for automatic trace propagation
response = http_utils.get("https://api.example.com/data")
response = http_utils.post("https://api.example.com/users", json={"name": "John"})

# Or use a traced session
session = http_utils.TracedSession()
response = session.get("https://api.example.com/data")
```

### SQS Message Propagation

```python
import boto3
from cl_logger import sqs_utils

# Wrap SQS client for automatic trace propagation
sqs = boto3.client('sqs')
traced_sqs = sqs_utils.TracedSQSClient(sqs)

# Send message with trace ID
traced_sqs.send_message(
    QueueUrl='https://sqs.region.amazonaws.com/account/queue',
    MessageBody='Hello World'
)

# Process incoming SQS message with trace context
def handle_message(message):
    logger.info("Processing message")
    # trace_id from message is automatically set

sqs_utils.process_sqs_message(sqs_message, handle_message)
```

## Configuration

### Environment Variables

- `CL_JSON_LOGGING`: Set to `"false"` to disable JSON logging (default: `"true"`)

### Programmatic Configuration

```python
from cl_logger import CLLogger

# Create logger with specific settings
logger = CLLogger(
    name="my_app",
    level="DEBUG",
    json_logging=True,  # Default
    log_to_file="app.log"
)

# Toggle to normal logging at runtime
logger.set_json_logging(False)

# Change log level
logger.set_level("WARNING")
```

## Output Examples

### JSON Logging (Default)
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "my_app",
  "message": "User action",
  "module": "views",
  "function": "login",
  "line": 42,
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123,
  "action": "login"
}
```

### Normal Logging
```
2024-01-15 10:30:45,123 - my_app - INFO - [550e8400-e29b-41d4-a716-446655440000] - User action | user_id=123 | action=login
```

## Django Integration

### Settings Configuration

In your Django settings:

```python
# settings.py
import os
from cl_logger import get_logger

# Logger for settings module
logger = get_logger(__name__)

# JSON logging is enabled by default
# To disable: export CL_JSON_LOGGING=false

# Middleware configuration
MIDDLEWARE = [
    # ...
    'content_lab_backend.middleware.logging_middleware.RequestLoggingMiddleware',
    # ...
]
```

### Usage in Views

```python
# views.py
from cl_logger import get_logger, get_trace_id

logger = get_logger(__name__)

def my_view(request):
    # Trace ID is automatically available from middleware
    logger.info("View accessed", extra={
        "user_id": request.user.id,
        "method": request.method,
        "path": request.path
    })
    
    # Access trace ID if needed
    trace_id = get_trace_id()
    # or
    trace_id = request.trace_id
```

## Advanced Usage

### Custom Logger Class

```python
from cl_logger import CLLogger

class AppLogger(CLLogger):
    def log_request(self, request_id, method, path, status, duration):
        self.info("API Request", extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status": status,
            "duration_ms": duration
        })

# Use custom logger
logger = AppLogger("api")
logger.log_request("abc123", "GET", "/api/users", 200, 45.2)
```

### Adding Trace Metadata

```python
from cl_logger import add_trace_metadata, get_trace_metadata

# Add metadata to current trace
add_trace_metadata("user_id", 123)
add_trace_metadata("tenant", "acme-corp")

# Metadata is automatically included in logs
logger.info("Processing request")
# Output includes: {..., "trace_metadata": {"user_id": 123, "tenant": "acme-corp"}}
```

## Best Practices

1. **Use Module Names**: Always use `__name__` for logger names
   ```python
   logger = get_logger(__name__)
   ```

2. **Structured Context**: Use `extra` parameter for structured data
   ```python
   logger.info("User action", extra={"user_id": 123, "action": "login"})
   ```

3. **Consistent Field Names**: Use consistent names for common fields
   - `user_id` for user identifiers
   - `request_id` or `trace_id` for request tracking
   - `duration_ms` for time measurements
   - `status` for operation results

4. **Let Middleware Handle Traces**: The middleware automatically manages trace IDs for HTTP requests

5. **Use Traced Clients for External Calls**: Use the provided utilities for external calls to maintain trace continuity

## Production Deployment

For production environments:

1. JSON logging is enabled by default (recommended)
2. Trace IDs are automatically propagated to Sentry
3. Use structured logging for better searchability and alerting
4. Configure your log aggregation service to parse JSON logs

## Troubleshooting

### Logs not appearing

1. Check the log level - by default, DEBUG messages are not shown
2. Ensure the logger is properly initialized: `logger = get_logger(__name__)`

### Trace IDs not propagating

1. Ensure middleware is properly configured
2. Use `http_utils` for HTTP requests or `sqs_utils` for SQS messages
3. Check that trace context is active: `get_trace_id()` should return a value

### Performance considerations

- The logger is lightweight and adds minimal overhead
- Trace context uses Python's contextvars for efficient async support
- Extra fields are only processed when actually logging

## License

MIT License - see LICENSE file for details. 