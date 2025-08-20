import re
from typing import Any, Dict, List, Type, Union

from fa_common.models import CamelModel


def deep_merge(base: Any, overlay: Any) -> Any:
    """
    Recursively merge properties of two complex objects.

    Args:
        base (Any): The base object, which provides default values.
        overlay (Any): The overlay object, whose values take precedence.

    Returns:
        Any: The result of deeply merged objects.
    """
    if isinstance(base, CamelModel) and isinstance(overlay, CamelModel):
        # Ensure both objects are instances of CamelModel before merging
        for field in base.model_fields:
            base_value = getattr(base, field)
            overlay_value = getattr(overlay, field, None)
            if overlay_value is not None:
                # Recursive merge if both are CamelModels, else overlay takes precedence
                if isinstance(base_value, CamelModel) and isinstance(overlay_value, CamelModel):
                    setattr(base, field, deep_merge(base_value, overlay_value))
                else:
                    setattr(base, field, overlay_value)
        return base
    elif isinstance(base, list) and isinstance(overlay, list):
        # Extend or replace lists
        return overlay  # This can be customized if you need to merge lists differently
    return overlay if overlay is not None else base


def parse_type(type_str: str) -> Type[Any]:
    # Base types mapping
    base_types = {"int": int, "float": float, "str": str, "bool": bool}

    # Handle Union types recursively
    if "Union" in type_str or "|" in type_str:
        parts = re.split(r"\s*\|\s*", type_str.replace("Union[", "").replace("]", ""))
        return Union[tuple(parse_type(part) for part in parts)]

    # Handle List, Set, Dict by recognizing the patterns
    if type_str.startswith("List["):
        inner_type = parse_type(type_str[5:-1])
        return List[inner_type]
    if type_str.startswith("Dict["):
        key_type, value_type = (part.strip() for part in type_str[5:-1].split(","))
        return Dict[parse_type(key_type), parse_type(value_type)]

    # Return the base type or default to str if not recognized
    if "object" in type_str:
        return type_str
    try:
        return base_types[type_str]
    except Exception as exc:
        raise ValueError(f"Unrecognized type: {type_str}") from exc


def camel_case_nested(param_name):
    return "".join([item.capitalize() for item in param_name.split("_")])
