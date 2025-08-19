# Finalsa SQS Consumer

A Python package for creating SQS message consumers in FastAPI applications with built-in dependency injection, interceptors, and async support.

## Features

- **SQS Message Consumption**: Simple, decorator-based SQS message handling
- **Worker-based Concurrency**: Concurrent message processing with configurable worker pools (like uvicorn)
- **Dependency Injection**: Built-in dependency injection system with `SqsDepends`
- **Async Support**: Full async/await support for message processing
- **Interceptors**: Pre/post-processing hooks for message handling
- **Signal Handling**: Graceful shutdown handling
- **Testing Support**: Built-in testing utilities
- **Type Safety**: Full type hints and validation

## Installation

```bash
pip install finalsa-sqs-consumer
```

## Quick Start

```python
from finalsa.sqs.consumer import SqsApp, SqsDepends

# Create app instance with worker-based concurrency
app = SqsApp(
    app_name="my-consumer",
    queue_url="https://sqs.region.amazonaws.com/account/queue-name",
    max_number_of_messages=10,
    workers=8  # 8 concurrent workers for high throughput
)

# Define a simple handler
@app.handler("user.created")
async def handle_user_created(message: dict):
    print(f"User created: {message}")

# Define handler with dependencies
@app.handler("order.created")
async def handle_order_created(
    message: dict,
    db_service: DatabaseService = SqsDepends(DatabaseService)
):
    await db_service.process_order(message)

# Run the consumer with concurrent workers
if __name__ == "__main__":
    app.run()  # Starts 8 worker processes
```

## Core Components

### SqsApp

Main application class that manages message consumption and routing.

```python
app = SqsApp(
    app_name="my-app",           # Application identifier
    queue_url="...",             # SQS queue URL
    max_number_of_messages=10,   # Max messages per batch
    workers=8,                   # Number of concurrent workers (like uvicorn)
    message_timeout=300.0,       # Message processing timeout in seconds (default: 5 minutes)
    interceptors=[]              # List of interceptor classes
)
```

**Worker-based Processing:**
- Messages are distributed to a pool of concurrent workers
- Each worker processes messages independently
- Similar to uvicorn's worker model for high throughput
- Automatic load balancing across workers
- Graceful shutdown of all workers

**Message Timeout:**
- Configurable timeout for processing individual messages
- Prevents workers from being blocked by long-running handlers
- Timed-out messages are logged and returned to queue for retry
- Default timeout: 300 seconds (5 minutes)

### Message Handlers

Register handlers for specific message topics:

```python
@app.handler("topic.name")
async def my_handler(message: dict, context: dict = None):
    # Process message
    pass
```
```

### Dependency Injection

Use `SqsDepends` for dependency injection:

```python
class MyService:
    def process(self, data): ...

@app.handler("topic")
async def handler(
    message: dict,
    service: MyService = SqsDepends(MyService)
):
    service.process(message)
```

### Interceptors

Create custom interceptors for cross-cutting concerns:

```python
from finalsa.sqs.consumer import AsyncConsumerInterceptor

class LoggingInterceptor(AsyncConsumerInterceptor):
    async def before_consume(self, topic: str, message: dict):
        print(f"Processing {topic}: {message}")
    
    async def after_consume(self, topic: str, result):
        print(f"Completed {topic}")

app = SqsApp(interceptors=[LoggingInterceptor])
```

## Message Timeout Configuration

Configure timeout limits for message processing to prevent workers from being blocked:

### Basic Timeout Configuration

```python
# Fast operations (API calls, simple DB operations)
fast_app = SqsApp(
    app_name="fast-processor",
    queue_url="...",
    workers=5,
    message_timeout=30.0  # 30 seconds
)

# Data processing operations
data_app = SqsApp(
    app_name="data-processor", 
    queue_url="...",
    workers=3,
    message_timeout=300.0  # 5 minutes (default)
)

# Heavy computation operations
heavy_app = SqsApp(
    app_name="heavy-processor",
    queue_url="...", 
    workers=2,
    message_timeout=1800.0  # 30 minutes
)
```

### Timeout Behavior

When a message handler exceeds the timeout:
- The handler execution is cancelled
- An error is logged with timeout details
- The message is **not** deleted from SQS (remains available for retry)
- The worker becomes available for new messages immediately

### Timeout Guidelines

- **Fast operations (5-60 seconds)**: API calls, simple DB operations, cache updates
- **Medium operations (1-10 minutes)**: File processing, image processing, data aggregation
- **Heavy operations (10-60 minutes)**: Large file processing, ML inference, complex data analysis

### Example Handler with Timeout

```python
# This handler has a 2-minute timeout
app = SqsApp(message_timeout=120.0)

@app.handler("data.process")
async def process_data(message: dict):
    # This operation must complete within 2 minutes
    # or it will be cancelled and logged as timeout
    await heavy_data_processing(message)
```

## Testing

Use `SqsAppTest` for testing message handlers:

```python
from finalsa.sqs.consumer import SqsAppTest

def test_user_handler():
    test_app = SqsAppTest(app)
    
    # Test handler
    result = test_app.test_handler(
        "user.created",
        {"user_id": 123, "name": "John"}
    )
    
    assert result is not None
```

## Error Handling

The library provides specific exceptions:

- `TopicNotFoundException`: Handler not found for topic
- `InvalidMessageException`: Message format validation failed
- `TopicAlreadyRegisteredException`: Duplicate topic registration

## Configuration

### Environment Variables

- `AWS_REGION`: AWS region for SQS
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

### Message Format

Expected SQS message format:

```json
{
  "topic": "user.created",
  "data": {
    "user_id": 123,
    "name": "John Doe"
  },
  "metadata": {
    "correlation_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Advanced Usage

### Custom Signal Handling

```python
from finalsa.sqs.consumer import SignalHandler

signal_handler = SignalHandler(logger)
# Automatic graceful shutdown on SIGTERM/SIGINT
```

### Concurrent Processing

Configure workers for high-throughput message processing:

```python
# High throughput configuration
app = SqsApp(
    app_name="high-throughput-service",
    queue_url="...",
    max_number_of_messages=10,  # Receive multiple messages per batch
    workers=16                  # 16 concurrent workers
)

@app.handler("bulk.process")
async def process_bulk_data(message: dict):
    # Each message processed by available worker
    await process_large_dataset(message)
```

### Multiple Workers

```python
app = SqsApp(workers=10)  # Process messages with 10 concurrent workers
```

**Benefits of Worker-based Processing:**
- **Concurrent Execution**: Multiple messages processed simultaneously
- **Fault Isolation**: Worker failures don't affect other workers
- **Load Balancing**: Messages automatically distributed to available workers
- **Graceful Shutdown**: All workers stop cleanly on termination signals
- **Better Throughput**: Ideal for I/O-bound operations like database calls

### Batch Processing

```python
app = SqsApp(max_number_of_messages=10)  # Receive up to 10 messages per batch
```

## Development

### Running Tests

```bash
pytest
```

### Linting

```bash
ruff check .
```

### Coverage

```bash
coverage run -m pytest
coverage report
```

## License

MIT License - see LICENSE.md for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## Requirements

- Python 3.10+
- AWS credentials configured
- SQS queue access

## Related Packages

- `finalsa-common-models`: Shared data models
- `finalsa-sqs-client`: SQS client implementation
- `finalsa-sns-client`: SNS client for notifications
- `finalsa-dependency-injector`: Dependency injection framework
