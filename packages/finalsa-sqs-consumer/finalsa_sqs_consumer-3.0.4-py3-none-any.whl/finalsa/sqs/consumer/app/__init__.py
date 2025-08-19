"""SQS Consumer application components.

This module contains the core implementation of the SQS consumer framework,
including the main application class, dependency injection system, exception
handling, and utility functions.

Key exports:
- SqsApp: Main SQS consumer application class
- SqsDepends: Dependency injection marker
- AsyncConsumerInterceptor: Base class for interceptors
- Exception classes for error handling
- Utility functions for message processing
"""

from .exceptions import (TopicAlreadyRegisteredException, InvalidMessageException,
                         TopicNotFoundException)
from .interceptors import AsyncConsumerInterceptor
from .build_sqs_depends import build_sqs_depends
from .get_function_attrs import get_function_attrs
from .get_missing_attrs import get_missing_attrs
from .base_model_attr import base_model_attr
from .dict_model_attr import dict_model_attr
from .signal_handler import SignalHandler
from .sqs_depends import SqsDepends
from .consumer import SqsConsumer
from .app import SqsApp


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
    "SqsConsumer"
]
