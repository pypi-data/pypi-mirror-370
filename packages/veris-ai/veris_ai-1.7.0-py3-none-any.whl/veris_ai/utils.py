import sys
import types
import typing
from contextlib import suppress
from typing import Any, ForwardRef, Literal, NotRequired, Required, Union, get_args, get_origin

from pydantic import BaseModel


def convert_to_type(value: object, target_type: type) -> object:
    """Convert a value to the specified type."""
    # Special case: Any type returns value as-is
    if target_type is Any:
        return value

    origin = get_origin(target_type)

    # Define conversion strategies for different type origins
    converters = {
        list: _convert_list,
        dict: _convert_dict,
        Union: _convert_union,
        types.UnionType: _convert_union,  # Handle Python 3.10+ union syntax (str | int)
    }

    # Use appropriate converter based on origin
    if origin in converters:
        return converters[origin](value, target_type)

    # Handle primitives and custom types
    return _convert_simple_type(value, target_type)


def _convert_list(value: object, target_type: type) -> list:
    """Convert a value to a typed list."""
    if not isinstance(value, list):
        error_msg = f"Expected list but got {type(value)}"
        raise ValueError(error_msg)

    item_type = get_args(target_type)[0]
    return [convert_to_type(item, item_type) for item in value]


def _convert_dict(value: object, target_type: type) -> dict:
    """Convert a value to a typed dict."""
    if not isinstance(value, dict):
        error_msg = f"Expected dict but got {type(value)}"
        raise ValueError(error_msg)

    key_type, value_type = get_args(target_type)
    return {convert_to_type(k, key_type): convert_to_type(v, value_type) for k, v in value.items()}


def _convert_union(value: object, target_type: type) -> object:
    """Try to convert value to one of the union types."""
    union_types = get_args(target_type)

    for possible_type in union_types:
        with suppress(ValueError, TypeError):
            return convert_to_type(value, possible_type)

    error_msg = f"Could not convert {value} to any of the union types {union_types}"
    raise ValueError(error_msg)


def _convert_simple_type(value: object, target_type: type) -> object:
    """Convert to primitive or custom types."""
    # Primitive types
    if target_type in (str, int, float, bool):
        return target_type(value)

    # Custom types - try kwargs for dicts, then direct instantiation
    if isinstance(value, dict):
        with suppress(TypeError):
            return target_type(**value)

    if target_type is types.NoneType:
        return None

    return target_type(value)


def _resolve_forward_ref(ref: ForwardRef, module_context: types.ModuleType | None = None) -> Any:  # noqa: ANN401
    """Resolve a ForwardRef to its actual type."""
    if not isinstance(ref, ForwardRef):
        return ref

    # Try to evaluate the forward reference
    try:
        # Get the module's namespace for evaluation
        namespace = dict(vars(module_context)) if module_context else {}

        # Add common typing imports to namespace
        namespace.update(
            {
                "Union": Union,
                "Any": Any,
                "Literal": Literal,
                "Required": Required,
                "NotRequired": NotRequired,
                "List": list,
                "Dict": dict,
                "Optional": typing.Optional,
                "Iterable": typing.Iterable,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            },
        )

        # Try to import from the same module to resolve local references
        if module_context and hasattr(module_context, "__name__"):
            with suppress(Exception):
                # Import all from the module to get access to local types
                exec(f"from {module_context.__name__} import *", namespace)  # noqa: S102

        # Get the forward reference string
        ref_string = ref.__forward_arg__ if hasattr(ref, "__forward_arg__") else str(ref)

        # Try to evaluate the forward reference string
        return eval(ref_string, namespace, namespace)  # noqa: S307
    except Exception:
        # If we can't resolve it, return the ref itself
        return ref


def _unwrap_required(field_type: Any) -> tuple[Any, bool]:  # noqa: ANN401
    """Unwrap Required/NotRequired and return the inner type and whether it's required."""
    origin = get_origin(field_type)

    # Check if it's Required or NotRequired
    if origin is Required:
        args = get_args(field_type)
        return args[0] if args else field_type, True
    if origin is NotRequired:
        args = get_args(field_type)
        return args[0] if args else field_type, False

    # Default to required for TypedDict fields
    return field_type, True


def extract_json_schema(target_type: Any) -> dict:  # noqa: PLR0911, PLR0912, C901, ANN401
    """Extract the JSON schema from a type or pydantic model.

    Args:
        target_type: The type or pydantic model to extract the JSON schema from.

    Returns:
        A dictionary representing the JSON schema.

    Example:
        >>> extract_json_schema(int)
        {"type": "integer"}

        >>> extract_json_schema(list[int])
        {"type": "array", "items": {"type": "integer"}}

        >>> extract_json_schema(list[User])
        {"type": "array", "items": {"type": "object", "properties": {...}}}
    """
    # Handle Pydantic BaseModel instances or classes
    if isinstance(target_type, type) and issubclass(target_type, BaseModel):
        return target_type.model_json_schema()
    if isinstance(target_type, BaseModel):
        return target_type.model_json_schema()

    # Handle TypedDict
    if (
        isinstance(target_type, type)
        and hasattr(target_type, "__annotations__")
        and hasattr(target_type, "__total__")
    ):
        # This is a TypedDict
        properties = {}
        required = []

        # Get the module context for resolving forward references
        module = sys.modules.get(target_type.__module__)

        for field_name, field_type_annotation in target_type.__annotations__.items():
            # Resolve forward references if present
            resolved_type = field_type_annotation
            if isinstance(resolved_type, ForwardRef):
                resolved_type = _resolve_forward_ref(resolved_type, module)

            # Unwrap Required/NotRequired
            unwrapped_type, is_required = _unwrap_required(resolved_type)

            # Extract schema for the unwrapped type
            properties[field_name] = extract_json_schema(unwrapped_type)

            # Add to required list if necessary
            if is_required and getattr(target_type, "__total__", True):
                required.append(field_name)

        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    # Handle built-in types
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        type(None): {"type": "null"},
        Any: {},  # Empty schema for Any type
    }

    if target_type in type_mapping:
        return type_mapping[target_type]

    # Handle generic types
    origin = get_origin(target_type)

    # Handle bare collection types
    if target_type is list:
        return {"type": "array"}
    if target_type is dict:
        return {"type": "object"}
    if target_type is tuple:
        return {"type": "array"}

    # Handle Literal types
    if origin is Literal:
        values = get_args(target_type)
        if len(values) == 1:
            # Single literal value - use const
            return {"const": values[0]}
        # Multiple literal values - use enum
        return {"enum": list(values)}

    if origin is list:
        args = get_args(target_type)
        if args:
            return {"type": "array", "items": extract_json_schema(args[0])}
        return {"type": "array"}

    if origin is dict:
        args = get_args(target_type)
        if len(args) == 2:  # noqa: PLR2004
            # For typed dicts like dict[str, int]
            return {
                "type": "object",
                "additionalProperties": extract_json_schema(args[1]),
            }
        return {"type": "object"}

    if origin is Union:
        args = get_args(target_type)
        # Handle Optional types (Union[T, None])
        if len(args) == 2 and type(None) in args:  # noqa: PLR2004
            non_none_type = args[0] if args[1] is type(None) else args[1]
            schema = extract_json_schema(non_none_type)
            return {"anyOf": [schema, {"type": "null"}]}
        # Handle general Union types
        return {"anyOf": [extract_json_schema(arg) for arg in args]}

    if origin is tuple:
        args = get_args(target_type)
        if args:
            return {
                "type": "array",
                "prefixItems": [extract_json_schema(arg) for arg in args],
                "minItems": len(args),
                "maxItems": len(args),
            }
        return {"type": "array"}

    # Default case for unknown types
    return {"type": "object"}
