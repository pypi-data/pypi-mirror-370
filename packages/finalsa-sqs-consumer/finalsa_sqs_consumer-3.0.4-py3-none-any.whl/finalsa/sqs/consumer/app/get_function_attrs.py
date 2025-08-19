"""Utility functions for extracting and mapping message attributes to handler parameters.

Provides functions to analyze handler function signatures and map message data
and metadata to the appropriate function parameters.
"""

from finalsa.sqs.consumer.app.base_model_attr import base_model_attr
from finalsa.sqs.consumer.app.dict_model_attr import dict_model_attr
from finalsa.common.models import AsyncMeta
from typing import Any, Dict


def get_function_attrs(
    message: Dict,
    meta: AsyncMeta,
    func_attrs: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Extract and map message attributes to handler function parameters.

    Analyzes the handler function's type hints and maps message data,
    metadata, and special attributes to the appropriate parameters.

    Args:
        message: The message payload dictionary
        meta: Message metadata including timestamps and correlation ID
        func_attrs: Dictionary of function parameter names and their type hints

    Returns:
        Dictionary mapping parameter names to their values for the handler

    Special parameters recognized:
        - timestamp: Mapped to meta.timestamp
        - correlation_id: Mapped to meta.correlation_id
        - meta: Mapped to the full AsyncMeta object
        - BaseModel subclasses: Message is parsed into the model
        - dict type: Raw message dictionary is passed
    """
    attrs_to_insert = {}
    if 'timestamp' in func_attrs:
        attrs_to_insert['timestamp'] = meta.timestamp
    if 'correlation_id' in func_attrs:
        attrs_to_insert['correlation_id'] = meta.correlation_id
    if 'meta' in func_attrs:
        attrs_to_insert['meta'] = meta
    base_model = base_model_attr(func_attrs)
    if base_model:
        attrs_to_insert[base_model[0]] = base_model[1](**message)
    dict_model = dict_model_attr(func_attrs)
    if dict_model:
        attrs_to_insert[dict_model[0]] = message
    return attrs_to_insert
