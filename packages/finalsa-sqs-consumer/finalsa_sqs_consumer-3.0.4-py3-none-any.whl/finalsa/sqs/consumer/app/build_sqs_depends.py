from typing import Any, Dict, Tuple, Callable
from finalsa.sqs.consumer.app.sqs_depends import SqsDepends


async def async_build_sqs_depends(
    fn_attrs: Dict[str, Any],
    get_async: Callable = None,
    defaults: Tuple = None,
    builded_dependencies: Dict[str, Any] = None,
) -> bool:
    attrs = {}

    def get_by_value(interface: Callable):
        for key in fn_attrs:
            if fn_attrs[key] == interface:
                return key
        return None
    for default in defaults:
        if isinstance(default, SqsDepends):
            key = get_by_value(default.interface)
            attrs[key] = get_async(default.interface, builded_dependencies)
    return attrs


def build_sqs_depends(
    fn_attrs: Dict[str, Any],
    get: Callable = None,
    defaults: Tuple = None,
    builded_dependencies: Dict[str, Any] = None,
) -> bool:
    attrs = {}
    def get_by_value(interface: Callable):
        for key in fn_attrs:
            if fn_attrs[key] == interface:
                return key
        return None
    if not defaults:
        defaults = []
    for default in defaults:
        if isinstance(default, SqsDepends):
            key = get_by_value(default.interface)
            if get:
                attrs[key] = get(default.interface, builded_dependencies)
    return attrs
