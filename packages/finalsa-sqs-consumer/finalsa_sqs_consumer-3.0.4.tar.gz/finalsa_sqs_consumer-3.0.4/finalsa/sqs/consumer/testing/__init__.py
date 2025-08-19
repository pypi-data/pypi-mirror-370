"""Testing utilities for SQS consumer applications.

Provides testing harnesses and mock implementations for unit testing
SQS message handlers without requiring actual AWS infrastructure.
"""

from .app import SqsAppTest

__all__ = [
    "SqsAppTest"
]