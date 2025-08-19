"""Utility functions for identifying missing handler function parameters.

Provides functions to determine which parameters need dependency injection
or default values based on what was extracted from the message.
"""

from typing import Dict, Any


def get_missing_attrs(
    received_attrs: Dict[str, Any],
    fn_attr: Dict[str, Any],
):
    """Identify handler parameters that need dependency injection or defaults.

    Compares the extracted message attributes against the handler's parameter
    types to determine which parameters still need values provided through
    dependency injection or default values.

    Args:
        received_attrs: Dictionary of parameters already extracted from message
        fn_attr: Dictionary of all handler function parameter names and types

    Returns:
        Dictionary of parameter names and types that still need values
    """
    missing_attrs = {}
    for attr in fn_attr:
        if attr not in received_attrs:
            missing_attrs[attr] = fn_attr[attr]
    return missing_attrs
