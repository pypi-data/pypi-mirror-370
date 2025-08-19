"""Testing utilities for SQS consumer applications.

Provides SqsAppTest class for testing message handlers without requiring
actual SQS infrastructure. Allows unit testing of handlers with mock
message data and metadata.
"""

from finalsa.traceability.context import set_context_from_w3c_headers, get_correlation_id
from finalsa.sqs.client import SqsServiceTest
from finalsa.sns.client import SnsClientTest
from finalsa.common.models import AsyncMeta
from finalsa.sqs.consumer.app import SqsApp
from asyncio import run
from typing import Any, Optional
from datetime import datetime, timezone


class SqsAppTest():
    """Test harness for SQS consumer applications.

    Provides utilities for testing message handlers without connecting to
    actual SQS queues. Automatically sets up mock SQS and SNS clients and
    provides methods to simulate message consumption.

    Attributes:
        app: The SqsApp instance to test

    Example:
        >>> app = SqsApp(app_name="test-app")
        >>> @app.handler("user.created")
        >>> async def handle_user(message: dict):
        ...     print(f"User: {message}")
        >>> 
        >>> test_app = SqsAppTest(app)
        >>> test_app.consume("user.created", {"user_id": 123})
    """

    def __init__(self, app: SqsApp) -> None:
        self.app = app

    def consume(
        self,
        topic: str,
        payload: Any,
        timestamp: Optional[datetime] = None,
        meta: Optional[AsyncMeta] = None,
    ):
        """Simulate consuming a message for testing purposes.

        Sets up mock clients and processes a message through the registered
        handler, allowing for unit testing without SQS infrastructure.

        Args:
            topic: The topic name to route the message to
            payload: The message payload to process
            timestamp: Optional timestamp for the message (defaults to now)
            meta: Optional custom AsyncMeta object (auto-generated if not provided)

        Example:
            >>> test_app.consume("user.created", {"user_id": 123, "name": "John"})
        """
        self.app.__sqs__ = SqsServiceTest()
        self.app.__sns__ = SnsClientTest()
        correlation_id = f"test-{topic}"
        set_context_from_w3c_headers(
            tracestate=f"finalsa={correlation_id}", app_name=self.app.app_name)
        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        if not meta:
            meta = AsyncMeta(
                topic=topic,
                timestamp=timestamp,
                correlation_id=get_correlation_id(),
                produced_at=timestamp,
                consumed_at=timestamp
            )
        run(self.app.process_message(payload, meta))
