"""Interceptor system for SQS message processing.

Provides an abstract base class for creating interceptors that can perform
pre/post-processing of messages, logging, validation, or other cross-cutting concerns.
"""

from finalsa.common.models import Meta
from abc import ABC, abstractmethod
from typing import Callable, Dict


class AsyncConsumerInterceptor(ABC):
    """Abstract base class for message processing interceptors.
    
    Interceptors allow you to implement cross-cutting concerns like logging,
    authentication, validation, or metrics collection that should run for
    all or specific message handlers.
    
    Example:
        >>> class LoggingInterceptor(AsyncConsumerInterceptor):
        ...     async def __call__(self, message: Dict, meta: Meta, call_next: Callable) -> Dict:
        ...         print(f"Processing {meta.topic}: {message}")
        ...         result = await call_next(message, meta)
        ...         print(f"Completed {meta.topic}")
        ...         return result
    """

    @abstractmethod
    async def __call__(self, message: Dict, meta: Meta, call_next: Callable) -> Dict:
        """Process a message with optional pre/post-processing.
        
        Args:
            message: The message payload to process
            meta: Message metadata including topic, timestamps, correlation ID
            call_next: Callable to continue the interceptor chain or invoke the handler
            
        Returns:
            The processed message or result from the handler
        """
        pass


def get_handler_interceptor(fn_handler) -> Callable[[Callable], AsyncConsumerInterceptor]:
    """Create an interceptor wrapper for a message handler function.
    
    Converts a regular handler function into an interceptor that can be
    used in the interceptor chain.
    
    Args:
        fn_handler: The handler function to wrap
        
    Returns:
        A class that creates interceptor instances for the handler
    """
    class HandlerInterceptor(AsyncConsumerInterceptor):
        async def __call__(self, message, meta, _):
            await fn_handler(message, meta)

    return HandlerInterceptor
