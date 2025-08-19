from typing import Any, Dict, List, Optional, Union, get_origin, get_args, TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal  # type: ignore
else:
    try:
        from typing import Literal
    except ImportError:
        try:
            from typing_extensions import Literal
        except ImportError:
            Literal = None
from os import getenv
from re import compile as compile_regex
from json import loads as json_loads
from enum import Enum
import sys

_builtin_field_re = compile_regex(r"^__[a-z][a-z0-9_]+__$")


class JsonObject:
    pass


def env_value_valid(val):
    return val != None and val != ""


def is_enum_type(field_type):
    """Check if a type is an enum class."""
    try:
        return isinstance(field_type, type) and issubclass(field_type, Enum)
    except TypeError:
        return False


def is_literal_type(field_type):
    """Check if a type is a Literal union."""
    if Literal is None:
        return False

    if sys.version_info >= (3, 8):
        origin = get_origin(field_type)
        return origin is Literal
    else:
        return getattr(field_type, "__origin__", None) is Literal


def parse_literal_value(field_type, value_str):
    """Parse a string value against a Literal type's allowed values."""
    if sys.version_info >= (3, 8):
        literal_values = get_args(field_type)
    else:
        literal_values = getattr(field_type, "__args__", ())

    # Try to match the string directly first
    if value_str in literal_values:
        return value_str

    # Try type conversions for each literal value
    for literal_val in literal_values:
        try:
            if isinstance(literal_val, bool):
                # Handle bool first since bool is a subclass of int in Python
                bool_val = value_str.lower() != "false" and value_str != "0"
                if bool_val == literal_val:
                    return literal_val
            elif isinstance(literal_val, str):
                if value_str == literal_val:
                    return literal_val
            elif isinstance(literal_val, int):
                if int(value_str) == literal_val:
                    return literal_val
            elif isinstance(literal_val, float):
                if float(value_str) == literal_val:
                    return literal_val
        except (ValueError, TypeError):
            continue

    # If no match found, raise ValueError
    raise ValueError(
        f"Value '{value_str}' is not one of the allowed literal values: {literal_values}"
    )


class BaseEnvironment:
    """
    Base class for environment-config objects.
    """

    def __init_subclass__(cls) -> None:
        annotations: Dict[str, Any] = cls.__dict__["__annotations__"]
        fields = filter(
            lambda x: _builtin_field_re.search(x) == None,
            annotations.keys(),
        )
        for field in fields:
            varname = field.upper()
            varval = getenv(varname)
            default_value = cls.__dict__.get(field, None)
            field_type = (
                annotations[field] if field in annotations else type(default_value)
            )
            v = None
            optional = False

            # optional case

            if field_type == Optional[bool]:
                optional = True
                if env_value_valid(varval):
                    assert varval is not None  # Type checker hint
                    v = varval.lower() != "false" and varval != "0"
            elif field_type == Optional[JsonObject]:
                optional = True
                if env_value_valid(varval):
                    assert varval is not None  # Type checker hint
                    v = json_loads(varval)
            else:
                # Check for Optional[Enum] - need to handle both Python 3.8+ and older versions
                if sys.version_info >= (3, 8):
                    origin = get_origin(field_type)
                    args = get_args(field_type)
                else:
                    origin = getattr(field_type, "__origin__", None)
                    args = getattr(field_type, "__args__", ())

                # Check if this is Optional/Union type
                if origin is Union and len(args) == 2 and type(None) in args:
                    inner_type = args[0] if args[1] is type(None) else args[1]
                    if is_enum_type(inner_type):
                        optional = True
                        if env_value_valid(varval):
                            v = inner_type(varval)
                    elif is_literal_type(inner_type):
                        optional = True
                        if env_value_valid(varval):
                            v = parse_literal_value(inner_type, varval)

                if not optional:
                    for typ in [str, int, float]:
                        if field_type == Optional[typ]:
                            optional = True
                            if env_value_valid(varval):
                                v = typ(varval)
                            break
                        elif field_type == Optional[List[typ]]:
                            optional = True
                            # overrides behavior of env_value_valid; empty string corresponds to empty list
                            if varval == "":
                                v = []
                            elif varval != None:
                                v = list(
                                    map(lambda x: typ(x.strip()), varval.split(","))
                                )
                            break

            # non-optional cases

            if not optional:
                if varval == None:
                    if default_value != None:
                        v = default_value
                    else:
                        raise RuntimeError(
                            f"Failed to load required environment variable `{varname}`"
                        )
                elif varval == "":
                    raise RuntimeError(
                        f"Environment variable `{varname}` is blank and not marked as optional; it must have a value"
                    )
                elif field_type == bool:
                    v = varval.lower() != "false" and varval != "0"
                elif field_type == JsonObject:
                    v = json_loads(varval)
                elif is_enum_type(field_type):
                    v = field_type(varval)
                elif is_literal_type(field_type):
                    v = parse_literal_value(field_type, varval)
                else:
                    for typ in [str, int, float]:
                        if field_type == typ:
                            v = field_type(varval)
                            break
                        elif field_type == list[typ] or field_type == List[typ]:
                            v = list(map(lambda x: typ(x.strip()), varval.split(",")))
                            break

                if v == None:
                    raise RuntimeError(
                        f"Unsupported type {field_type} for field {field}"
                    )

            setattr(cls, field, v)

    @classmethod
    def refresh(cls) -> None:
        """
        Refresh the environment-config object.
        """
        cls.__init_subclass__()
