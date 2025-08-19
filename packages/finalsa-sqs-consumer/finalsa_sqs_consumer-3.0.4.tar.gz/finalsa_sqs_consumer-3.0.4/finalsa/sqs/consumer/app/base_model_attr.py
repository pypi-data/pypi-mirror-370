from typing import Dict, Any, Optional, Tuple, Type
from finalsa.common.models import AsyncMeta, Meta
from pydantic import BaseModel


def base_model_attr(attrs: Dict[str, Any]) -> Optional[Tuple[Dict, BaseModel]]:
    for attr_name in attrs:
        if attr_name == "return":
            continue
        if attr_name == "meta":
            continue
        attr_type: Type = attrs[attr_name]
        if attr_type is Meta:
            continue
        if attr_type is AsyncMeta:
            continue
        if issubclass(attr_type, BaseModel):
            return attr_name, attr_type
    return None
