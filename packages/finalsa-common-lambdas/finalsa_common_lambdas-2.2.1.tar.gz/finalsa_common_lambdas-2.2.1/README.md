# Finalsa Common Lambda

[![Version](https://img.shields.io/badge/version-2.0.4-blue.svg)](https://pypi.org/project/finalsa-common-lambdas/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Type Hints](https://img.shields.io/badge/typing-fully%20typed-green.svg)](https://docs.python.org/3/library/typing.html)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)

A comprehensive, **type-safe** Python library for building AWS Lambda functions with common patterns, utilities, and best practices for the Finalsa ecosystem.

## 🚀 Features

- **🔒 Full Type Safety**: Comprehensive type hints for better IDE support and error detection
- **🌐 Unified Lambda Framework**: Simple, decorator-based approach for handling both HTTP and SQS events
- **🎯 Type Safety**: Full type hints and Pydantic model integration with protocols and generics
- **📊 Built-in Traceability**: Automatic correlation ID and trace management
- **⚡ Error Handling**: Robust exception handling with retries and logging
- **🧪 Test Support**: Built-in test mode with mocking capabilities and type-safe testing
- **🔧 Modular Design**: Composable handlers for different event types
- **💡 Developer Experience**: Excellent IDE support with auto-completion and type checking

## 📦 Installation

```bash
pip install finalsa-common-lambdas
```

## 🏗️ Quick Start

### Basic Lambda Function with Type Safety

```python
from finalsa.common.lambdas.app import App
from typing import Dict, Any, Union
from finalsa.common.lambdas.http.HttpResponse import HttpResponse

# Create your lambda handler
class MyLambda(AppEntry):
    pass

# Create app instance
app = App("my-lambda-function")

# Register SQS handlers
@app.sqs.default()
def handle_default_sqs(message: dict):
    print(f"Processing message: {message}")
    return {"status": "processed"}

@app.sqs.handler("user-events")
def handle_user_events(message: dict, meta: dict):
    print(f"User event: {message}")
    return {"status": "success"}

# Register HTTP handlers
@app.http.post("/users")
def create_user(body: dict):
    return {"message": "User created", "id": 123}

@app.http.get("/users/{user_id}")
def get_user(user_id: str):
    return {"user_id": user_id, "name": "John Doe"}

# Lambda entry point
def lambda_handler(event, context):
    return app.execute(event, context)
```

### Using AppEntry for Modular Design

```python
from finalsa.common.lambdas.app import App, AppEntry

# Create modular app entries
user_service = AppEntry("user-service")
notification_service = AppEntry("notification-service")

# Define handlers in user service
@user_service.http.post("/users")
def create_user(body: dict):
    return {"message": "User created"}

@user_service.sqs.handler("user-created")
def handle_user_created(message: dict):
    print("User created event processed")

# Define handlers in notification service
@notification_service.sqs.handler("send-email")
def send_email(message: dict):
    print("Sending email...")

# Combine into main app
app = App("main-app")
app.register(user_service)
app.register(notification_service)

def lambda_handler(event, context):
    return app.execute(event, context)
```

## 📖 Documentation

### Core Components

#### App Class

The main application container that manages multiple `AppEntry` instances.

```python
from finalsa.common.lambdas.app import App

app = App(
    app_name="my-lambda",           # Optional: name for logging
    logger=custom_logger,           # Optional: custom logger
    test_mode=False                 # Optional: enable test mode
)
```

**Methods:**
- `register(app_entry)`: Register an AppEntry with the app
- `execute(event, context)`: Main entry point for Lambda execution

#### AppEntry Class

Base class for creating modular Lambda handlers.

```python
from finalsa.common.lambdas.app import AppEntry

entry = AppEntry(
    app_name="my-service",         # Optional: service name
    logger=custom_logger           # Optional: custom logger
)
```

**Properties:**
- `sqs`: SQS handler instance
- `http`: HTTP handler instance

### SQS Handler

Handle SQS events with automatic message parsing and error handling.

#### Basic Usage

```python
# Default handler (catches all unmatched topics)
@app.sqs.default()
def handle_default(message: dict):
    return {"status": "processed"}

# Topic-specific handler
@app.sqs.handler("user-events")
def handle_user_events(message: dict):
    return {"status": "success"}

# Handler with metadata
@app.sqs.handler("orders", retries=3)
def handle_orders(message: dict, meta: dict):
    correlation_id = meta.get("correlation_id")
    return {"order_id": message["id"]}
```

#### Available Parameters

Your SQS handler functions can accept these parameters:

- `message: dict` - Parsed message body
- `meta: dict` - Message metadata (correlation_id, trace_id, etc.)
- `event: SqsEvent` - Raw SQS event object
- `context` - Lambda context object

#### Error Handling and Retries

```python
@app.sqs.handler("critical-process", retries=5)
def handle_critical(message: dict):
    # This will retry up to 5 times on failure
    if not process_critical_data(message):
        raise Exception("Processing failed")
    return {"status": "success"}
```

### HTTP Handler

Handle HTTP API Gateway events with automatic routing and parameter extraction.

#### HTTP Methods

```python
# Basic routes
@app.http.get("/health")
def health_check():
    return {"status": "healthy"}

@app.http.post("/users")
def create_user(body: dict):
    return {"user_id": 123}

@app.http.put("/users/{user_id}")
def update_user(user_id: str, body: dict):
    return {"user_id": user_id, "updated": True}

@app.http.delete("/users/{user_id}")
def delete_user(user_id: str):
    return {"deleted": True}
```

#### Path Parameters

```python
# Single path parameter
@app.http.get("/users/{user_id}")
def get_user(user_id: str):
    return {"user_id": user_id}

# Multiple path parameters
@app.http.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: str, post_id: str):
    return {"user_id": user_id, "post_id": post_id}
```

#### Available Parameters

Your HTTP handler functions can accept these parameters:

- `body: dict` - Parsed request body
- `headers: dict` - Request headers
- `query: dict` - Query string parameters
- `path_params: dict` - Path parameters
- `meta: dict` - Request metadata
- `event: dict` - Raw API Gateway event
- `context` - Lambda context object

#### Custom Response Codes

```python
from finalsa.common.lambdas.http.HttpResponse import HttpResponse

@app.http.post("/users")
def create_user(body: dict):
    # Custom status code
    return HttpResponse(
        status_code=201,
        body={"user_id": 123},
        headers={"Location": "/users/123"}
    )

@app.http.get("/users/{user_id}")
def get_user(user_id: str):
    if not user_exists(user_id):
        return HttpResponse(
            status_code=404,
            body={"error": "User not found"}
        )
    return {"user_id": user_id}
```

## 🧪 Testing

### Test Mode

Enable test mode to use mocked services:

```python
from finalsa.common.lambdas.app import App

# Enable test mode
app = App(test_mode=True)

# Or enable later
app.__set_test_mode__()

# Test your handlers
response = app.execute({
    "eventSource": "aws:sqs",
    "Records": [
        {
            "body": '{"test": "message"}',
            "messageAttributes": {
                "correlation_id": {
                    "stringValue": "test-correlation-id"
                }
            }
        }
    ]
})
```

### Example Test

```python
import pytest
from finalsa.common.lambdas.app import App, AppEntry

def test_sqs_handler():
    # Setup
    app_entry = AppEntry()
    
    @app_entry.sqs.default()
    def handle_message(message: dict):
        return {"processed": message["id"]}
    
    app = App(test_mode=True)
    app.register(app_entry)
    
    # Test
    event = {
        "eventSource": "aws:sqs",
        "Records": [
            {
                "body": '{"id": "123", "type": "test"}',
                "messageAttributes": {}
            }
        ]
    }
    
    result = app.execute(event)
    assert result[0]["processed"] == "123"

def test_http_handler():
    app_entry = AppEntry()
    
    @app_entry.http.get("/users/{user_id}")
    def get_user(user_id: str):
        return {"user_id": user_id}
    
    app = App(test_mode=True)
    app.register(app_entry)
    
    event = {
        "httpMethod": "GET",
        "path": "/users/123",
        "pathParameters": {"user_id": "123"}
    }
    
    result = app.execute(event)
    assert result["statusCode"] == 200
```

## 🏗️ Architecture

### Event Flow

```
Lambda Event → App.execute() → Handler Detection → Route to SQS/HTTP → Handler Execution → Response
```

### Component Structure

```
App
├── AppEntry (modular services)
│   ├── SqsHandler (message processing)
│   └── HttpHandler (API routing)
├── Traceability (correlation/trace IDs)
├── Error Handling (retries, logging)
└── Test Support (mocking, fixtures)
```

## 🔧 Advanced Usage

### Custom Error Handling

```python
from finalsa.common.lambdas.common.exceptions import HandlerNotFoundError

@app.sqs.handler("critical-data")
def handle_critical(message: dict):
    try:
        process_data(message)
    except ValueError as e:
        # Log and re-raise for retry
        app.logger.error(f"Invalid data: {e}")
        raise
    except Exception as e:
        # Handle gracefully
        app.logger.warning(f"Processing failed: {e}")
        return {"status": "failed", "error": str(e)}
```

### Custom Logging

```python
import logging
from finalsa.common.lambdas.app import App

# Custom logger
logger = logging.getLogger("my-app")
logger.setLevel(logging.INFO)

app = App("my-lambda", logger=logger)
```

### Environment Configuration

```python
import os
from finalsa.common.lambdas.app import App

app = App(
    app_name=os.getenv("APP_NAME", "default-app"),
    test_mode=os.getenv("TEST_MODE", "false").lower() == "true"
)
```

## 🤝 Dependencies

This library depends on several Finalsa internal packages:

- `finalsa-common-logger` - Logging utilities
- `finalsa-common-models` - Pydantic models
- `finalsa-sqs-client` - SQS client implementation
- `finalsa-traceability` - Tracing and correlation
- `orjson` - Fast JSON parsing
- `pydantic` - Data validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🔗 Links

- [Homepage](https://github.com/finalsa/finalsa-common-lambda)
- [PyPI Package](https://pypi.org/project/finalsa-common-lambdas/)
- [Documentation](https://github.com/finalsa/finalsa-common-lambda/wiki)

## 📞 Support

For questions and support, please contact [luis@finalsa.com](mailto:luis@finalsa.com)
