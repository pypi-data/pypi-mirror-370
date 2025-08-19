"""Finalsa SQS Consumer - A Python package for SQS message consumption with dependency injection.

This package provides a decorator-based API for creating SQS message consumers
with built-in support for:
- Async message processing
- Dependency injection
- Interceptors for cross-cutting concerns
- Graceful shutdown handling
- Testing utilities

Main components:
- SqsApp: Main application class for SQS message consumption
- SqsDepends: Dependency injection marker
- AsyncConsumerInterceptor: Base class for interceptors
- SqsAppTest: Testing utilities

Example:
    >>> from finalsa.sqs.consumer import SqsApp, SqsDepends
    >>> 
    >>> app = SqsApp(
    ...     app_name="my-service",
    ...     queue_url="https://sqs.region.amazonaws.com/account/queue"
    ... )
    >>> 
    >>> @app.handler("user.created")
    >>> async def handle_user_created(message: dict):
    ...     print(f"User created: {message}")
    >>> 
    >>> app.run()
"""

from finalsa.sqs.consumer.app import (
    SqsDepends,
    build_sqs_depends,
    get_function_attrs,
    get_missing_attrs,
    base_model_attr,
    dict_model_attr,
    SignalHandler,
    TopicAlreadyRegisteredException,
    InvalidMessageException,
    TopicNotFoundException,
    SqsApp,
    AsyncConsumerInterceptor,
    SqsConsumer
)

from finalsa.sqs.consumer.testing import SqsAppTest


__all__ = [
    "SqsDepends",
    "build_sqs_depends",
    "get_function_attrs",
    "get_missing_attrs",
    "base_model_attr",
    "dict_model_attr",
    "SignalHandler",
    "TopicAlreadyRegisteredException",
    "InvalidMessageException",
    "TopicNotFoundException",
    "AsyncConsumerInterceptor",
    "SqsApp",
    "SqsAppTest",
    "SqsConsumer"
]
