"""Base SQS consumer class providing handler registration and message routing.

Provides the core functionality for registering message handlers and routing
messages to appropriate handlers based on topic names.
"""

from finalsa.sqs.consumer.app.get_function_attrs import get_function_attrs
from finalsa.sqs.consumer.app.get_missing_attrs import get_missing_attrs
from finalsa.sqs.consumer.app.build_sqs_depends import build_sqs_depends
from finalsa.sqs.consumer.app.exceptions import (
    TopicAlreadyRegisteredException
)
from typing import Dict, Callable, get_type_hints, Any
from finalsa.common.models import AsyncMeta
from logging import getLogger, Logger
from asyncio import sleep


class SqsConsumer():
    """Base class for SQS message consumers.
    
    Provides handler registration, dependency injection, and message routing
    capabilities. This class is extended by SqsApp to add SQS-specific
    message consumption functionality.
    
    Attributes:
        __handlers__: Dictionary mapping topic names to handler functions
        logger: Logger instance for the consumer
    """

    __handlers__: Dict[str, Callable]

    def __init__(
        self,
    ) -> None:
        self.__handlers__: Dict[str, Callable] = {}
        self.logger: Logger = getLogger("finalsa.sqs.consumer")

    def include_consumer(self, consumer: 'SqsConsumer'):
        """Include handlers from another consumer instance.
        
        Merges handlers from another consumer into this one, allowing
        for modular handler organization.
        
        Args:
            consumer: Another SqsConsumer instance to include
            
        Raises:
            TopicAlreadyRegisteredException: If a topic is already registered
        """
        for topic in consumer.__handlers__:
            if topic in self.__handlers__:
                raise TopicAlreadyRegisteredException(topic)
            self.__handlers__[topic] = consumer.__handlers__[topic]
        consumer.logger = self.logger

    async def __call_handler__(
        self,
        handler: Callable,
        request_attrs:  Dict[str, Any],
        missing_attrs: Dict[str, Any],
        function_defaults: Dict[str, Any],
        meta: AsyncMeta,
        retries: int,
        retry_delay: int
    ):
        dependencies = build_sqs_depends(
            missing_attrs,
            None,
            function_defaults,
            builded_dependencies={}
        )
        for i in range(retries):
            try:
                attrs = {
                    **request_attrs,
                    **dependencies
                }
                await handler(**attrs)
                break
            except Exception as ex:
                self.logger.error(
                    f"Error processing message for topic {meta.topic} retrying {i+1} of {retries}")
                self.logger.exception(ex)
                if (i == retries - 1):
                    self.logger.error(
                        f"Error processing message for topic {meta.topic} max retries reached")
                    raise ex
                await sleep(retry_delay)

    def __decorator__(self, topic: str = '', retries: int = 10, retry_delay: int = 3):
        self.logger.info(f"Adding handler for topic {topic}")

        def decorator(handler: Callable):
            function_attrs = get_type_hints(handler)
            function_defaults = handler.__defaults__

            async def async_wrapper(message: Dict, meta: AsyncMeta):
                request_attrs = get_function_attrs(message, meta, function_attrs)
                missing_attrs = get_missing_attrs(
                    request_attrs, function_attrs)
                await self.__call_handler__(
                    handler, request_attrs, missing_attrs, function_defaults, meta, retries, retry_delay
                )

            self.__handlers__[topic] = async_wrapper
        return decorator

    def handler(self, topic: str = '', retries: int = 1, retry_delay: int = 1):
        """Decorator to register a message handler for a specific topic.
        
        Args:
            topic: Topic name to handle (e.g., "user.created", "order.processed")
            retries: Number of retry attempts on handler failure (default: 1)
            retry_delay: Delay in seconds between retry attempts (default: 1)
            
        Returns:
            Decorator function that registers the handler
            
        Example:
            >>> @app.handler("user.created", retries=3, retry_delay=2)
            >>> async def handle_user_created(message: dict):
            ...     print(f"User created: {message}")
        """
        return self.__decorator__(topic, retries, retry_delay)
