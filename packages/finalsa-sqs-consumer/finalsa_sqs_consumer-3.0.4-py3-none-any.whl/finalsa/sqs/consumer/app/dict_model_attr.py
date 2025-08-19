from typing import Dict, Any, Tuple, Optional, Type
from pydantic import BaseModel


def dict_model_attr(attrs: Dict[str, Any]) -> Optional[Tuple[Dict, BaseModel]]:
    for attr_name in attrs:
        if attr_name == "return":
            continue
        attr_type: Type = attrs[attr_name]
        if attr_type is dict:
            return attr_name, attr_type
    return None
