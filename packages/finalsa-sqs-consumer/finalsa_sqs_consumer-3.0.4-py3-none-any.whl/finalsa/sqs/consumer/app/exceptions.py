"""Exception classes for SQS consumer error handling.

Defines specific exceptions that can occur during SQS message processing,
including invalid message formats, missing handlers, and duplicate registrations.
"""

from orjson import dumps


class InvalidMessageException(Exception):
    """Raised when a received SQS message has invalid format or missing required fields.

    This exception is thrown when:
    - Message is missing the 'topic' field
    - Message format doesn't match expected structure
    - Required message attributes are missing
    """

    def __init__(self, attrs, body) -> None:
        super().__init__(
            f'Topic not found in message attributes {dumps(attrs)} or body {dumps(body)}')


class TopicAlreadyRegisteredException(Exception):
    """Raised when attempting to register a handler for a topic that already has a handler.
    
    Each topic can only have one handler registered. This exception prevents
    accidental handler overwrites and ensures clear message routing.
    """

    def __init__(self, topic) -> None:
        super().__init__(f"Topic {topic} already registered in this consumer")


class TopicNotFoundException(Exception):
    """Raised when a message is received for a topic with no registered handler.
    
    This indicates either:
    - A handler was not registered for the topic
    - The topic name in the message doesn't match any registered handlers
    - Message routing configuration is incorrect
    """

    def __init__(self, topic) -> None:
        super().__init__(f"Handler not found for topic {topic}")
