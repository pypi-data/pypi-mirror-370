"""SQS Consumer application for processing messages from AWS SQS queues.

This module provides the main SqsApp class for creating SQS message consumers
with dependency injection, interceptors, and async message processing support.
"""

from finalsa.common.models import SqsReponse, AsyncMeta
from finalsa.sqs.consumer.app.signal_handler import SignalHandler
from finalsa.sqs.consumer.app.consumer import SqsConsumer
from finalsa.sqs.consumer.app.interceptors import (AsyncConsumerInterceptor,
                                                   get_handler_interceptor)
from finalsa.sqs.consumer.app.exceptions import (
    InvalidMessageException, TopicNotFoundException
)
from finalsa.sqs.consumer.app.executor import Executor
from finalsa.traceability import set_context_from_w3c_headers, get_correlation_id, HTTP_HEADER_TRACEPARENT, HTTP_HEADER_TRACESTATE
from finalsa.sqs.client import (
    SqsServiceImpl, SqsService)
from finalsa.sns.client import (
    SnsClient, SnsClientImpl)
from typing import Dict, List, Callable
from datetime import datetime, timezone
from logging import getLogger, Logger
from asyncio import sleep, run, create_task, gather, Queue, Event, Task
import time
import asyncio

TOPIC_NAME = 'X-Topic'
SUBTOPIC_NAME = 'X-Subtopic'
PRODUCED_AT = 'X-Produced-At'
RETRY_COUNT = 'X-Retry-Count'


class SqsApp(SqsConsumer):
    """Main SQS consumer application class with worker-based concurrent processing.

    Manages SQS message consumption, routing to handlers, dependency injection,
    and interceptor execution. Uses a worker pool similar to uvicorn for concurrent
    message processing. Provides a decorator-based API for registering message 
    handlers and supports graceful shutdown.

    Attributes:
        app_name: Application identifier for logging and traceability
        sqs_url: SQS queue URL to consume from
        sqs_max_number_of_messages: Maximum messages to receive per batch
        workers: Number of concurrent workers for message processing
        message_timeout: Maximum time in seconds to process a single message
        logger: Logger instance for the consumer

    Example:
        >>> app = SqsApp(
        ...     app_name="user-service",
        ...     queue_url="https://sqs.us-east-1.amazonaws.com/123/users",
        ...     max_number_of_messages=10,
        ...     workers=5,  # 5 concurrent workers
        ...     message_timeout=60.0  # 60 second timeout per message
        ... )
        >>> 
        >>> @app.handler("user.created")
        >>> async def handle_user(message: dict):
        ...     print(f"User created: {message}")
        ...     # This handler has 60 seconds to complete
        >>> 
        >>> app.run()  # Starts with 5 concurrent workers and 60s timeout
    """

    __sqs__: SqsService
    __sns__: SnsClient
    __handlers__: Dict[str, Callable]
    __interceptors__: List[AsyncConsumerInterceptor]
    __message_queue__: Queue
    __worker_tasks__: List[Task]
    __shutdown_event__: Event

    def __init__(
        self,
        app_name: str = '',
        queue_url: str = '',
        max_number_of_messages: int = 1,
        workers: int = 5,
        message_timeout: float = 300.0,
        interceptors: List[AsyncConsumerInterceptor] = []
    ) -> None:
        """Initialize SQS consumer application with worker-based processing.

        Args:
            app_name: Application identifier for logging and traceability
            queue_url: SQS queue URL to consume messages from
            max_number_of_messages: Maximum number of messages to receive per batch (1-10)
            workers: Number of concurrent workers for message processing (like uvicorn workers)
            message_timeout: Maximum time in seconds to process a single message (default: 300s/5min)
            interceptors: List of interceptor classes for pre/post-processing

        Note:
            The worker system creates a pool of async tasks that process messages
            concurrently, similar to how uvicorn handles concurrent requests.
            Each worker processes messages independently from a shared queue.

            The message_timeout parameter controls how long a worker will wait for
            a message to be processed before timing out. This prevents workers from
            getting stuck on long-running or hanging message handlers.
        """
        self.app_name = app_name
        self.sqs_url = queue_url
        self.sqs_max_number_of_messages = max_number_of_messages
        self.__handlers__: Dict[str, Callable] = {}
        self.logger: Logger = getLogger("finalsa.sqs.consumer")
        self.__signal_handler__ = SignalHandler(self.logger)
        self.workers = workers
        self.message_timeout = message_timeout
        self.__interceptors__ = []
        for interceptor in interceptors:
            self.__interceptors__.append(interceptor())

        # Worker infrastructure
        self.__message_queue__: Queue = Queue(
            maxsize=self.workers * 10)  # Buffer size
        self.__worker_tasks__: List[Task] = []
        self.__shutdown_event__: Event = Event()

    def run(self):
        """Start the SQS consumer and begin processing messages.

        Initializes SQS and SNS clients, subscribes to topics, and starts
        the main message consumption loop. Blocks until a shutdown signal is received.
        """
        self.__sqs__: SqsService = SqsServiceImpl()
        self.__sns__: SnsClient = SnsClientImpl()
        self.logger.info("Running consumer")
        run(self.__start__())
        self.logger.info("Consumer stopped")

    def __stop__(self):
        """Stop the consumer and all workers gracefully."""
        self.logger.info("Stopping consumer")
        self.__signal_handler__.received_signal = True
        self.__shutdown_event__.set()

    async def __worker__(self, worker_id: int):
        """Individual worker that processes messages from the queue.

        Args:
            worker_id: Unique identifier for this worker
        """
        self.logger.info(f"Worker {worker_id} started")

        while not self.__shutdown_event__.is_set():
            try:
                # Wait for a message with timeout to allow checking shutdown event
                try:
                    response = await asyncio.wait_for(
                        self.__message_queue__.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Process the message with timeout
                try:
                    self.logger.debug(f"Worker {worker_id} processing message")

                    # Apply timeout to message processing
                    await asyncio.wait_for(
                        self.__set_context_and_process_message__(response),
                        timeout=self.message_timeout
                    )

                    # Delete message from SQS after successful processing
                    self.__sqs__.delete_message(
                        self.sqs_url, response.receipt_handle
                    )
                    self.logger.debug(f"Worker {worker_id} completed message")

                except asyncio.TimeoutError:
                    self.logger.error(f"Worker {worker_id}: Message processing timeout after {self.message_timeout}s", extra={
                        "message_id": getattr(response, 'message_id', 'unknown'),
                        "timeout": self.message_timeout
                    })
                    # Don't delete message on timeout - let it go back to queue for retry
                except InvalidMessageException as ex:
                    self.logger.error(
                        f"Worker {worker_id}: Invalid message received")
                    self.logger.exception(ex)
                    # Delete message from SQS on invalid message
                    self.__sqs__.delete_message(
                        self.sqs_url, response.receipt_handle
                    )
                except Exception as ex:
                    self.logger.error(f"Worker {worker_id}: Error processing message", extra={
                        "message_id": getattr(response, 'message_id', 'unknown')
                    })
                    self.logger.exception(ex)
                finally:
                    # Mark task as done
                    self.__message_queue__.task_done()

            except Exception as ex:
                self.logger.error(
                    f"Worker {worker_id}: Unexpected error", exc_info=ex)
                await sleep(1)  # Brief pause before continuing

        self.logger.info(f"Worker {worker_id} stopped")

    async def __start_workers__(self):
        """Start all worker tasks."""
        self.logger.info(f"Starting {self.workers} workers")

        # Clear any existing worker tasks first
        self.__worker_tasks__.clear()

        for worker_id in range(self.workers):
            task = create_task(
                self.__worker__(worker_id),
                name=f"sqs-worker-{worker_id}"
            )
            self.__worker_tasks__.append(task)

        self.logger.info(f"All {self.workers} workers started")

    async def __stop_workers__(self):
        """Stop all worker tasks gracefully."""
        self.logger.info("Stopping workers...")

        # Signal all workers to stop
        self.__shutdown_event__.set()

        # Wait for all workers to complete
        if self.__worker_tasks__:
            await gather(*self.__worker_tasks__, return_exceptions=True)

        self.logger.info("All workers stopped")

    def __subscribe__(self):
        for key in self.__handlers__:
            self.__sns__.get_or_create_topic(key)
            arn = self.__sqs__.get_queue_arn(self.sqs_url)
            if not self.__sns__.subscription_exists(key, arn):
                self.__sns__.subscribe(key, "sqs", arn)

    async def __start__(self):
        """Start the consumer with worker-based message processing."""
        self.logger.info("Starting consumer with worker-based processing")
        self.__subscribe__()

        # Start worker tasks
        await self.__start_workers__()

        try:
            # Main message receiving loop
            while not self.__signal_handler__.received_signal and not self.__shutdown_event__.is_set():
                self.logger.debug("Receiving messages")
                await self.__receive_messages__()

        finally:
            # Cleanup: stop workers gracefully
            await self.__stop_workers__()

    async def __receive_messages__(self):
        """Receive messages from SQS and distribute them to workers."""
        try:
            messages = self.__sqs__.receive_messages(
                queue_url=self.sqs_url,
                max_number_of_messages=self.sqs_max_number_of_messages,
                wait_time_seconds=1
            )

            if not messages or len(messages) == 0:
                await sleep(0.1)  # Short sleep when no messages
                return

            self.logger.info(
                f"Received {len(messages)} messages, distributing to workers")

            # Distribute messages to worker queue
            for message in messages:
                await self.__message_queue__.put(message)

        except Exception as ex:
            self.logger.error("Error receiving messages", exc_info=ex)
            await sleep(1)  # Brief pause on error

    async def process_message(self, message: Dict, meta: AsyncMeta):
        """Process a single SQS message.

        Args:
            message: The message payload to process
            meta: Message metadata including topic, timestamps, correlation ID

        Raises:
            TopicNotFoundException: If no handler is registered for the message topic
        """
        start_time = time.time()
        self.logger.info("Processing message", extra={
            "topic": meta.topic
        })
        await self.__process_message__(message, meta)
        end_time = time.time()
        self.logger.info(f"Message processed in {end_time-start_time} seconds", extra={
            "topic": meta.topic
        })

    async def __process_message__(self, message: Dict, meta: AsyncMeta):
        if meta.topic not in self.__handlers__:
            self.logger.error(
                f"No handler found for topic {meta.topic}")
            raise TopicNotFoundException(meta.topic)
        fn_handler = self.__handlers__[meta.topic]
        handler_interceptor = get_handler_interceptor(fn_handler)
        interceptors = []
        for interceptor in self.__interceptors__:
            interceptors.append(interceptor)
        interceptors.append(handler_interceptor())
        executor = Executor(interceptors)
        await executor.call(message, meta)

    async def __set_context_and_process_message__(self, response: SqsReponse):
        payload = response.get_payload()
        message_attributes = response.message_attributes if response.message_attributes else {}
        set_context_from_w3c_headers(
            message_attributes.get(HTTP_HEADER_TRACEPARENT),
            message_attributes.get(HTTP_HEADER_TRACESTATE),
            self.app_name
        )
        actual_datetime = datetime.now(timezone.utc)
        meta = AsyncMeta(
            topic=response.topic,
            timestamp=actual_datetime,
            subtopic=response.message_attributes.get(
                SUBTOPIC_NAME, None
            ),
            correlation_id=get_correlation_id(),
            produced_at=response.message_attributes.get(
                PRODUCED_AT, actual_datetime
            ),
            consumed_at=actual_datetime,
            retry_count=response.message_attributes.get(
                RETRY_COUNT, 0
            ),
        )
        try:
            return await self.process_message(payload, meta)
        except Exception as ex:
            self.logger.error("Error processing message", exc_info=ex)
            self.logger.exception(ex)
