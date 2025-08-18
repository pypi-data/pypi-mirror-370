from typing import Any, Dict, List, Optional
from os import getenv
from re import compile as compile_regex
from json import loads as json_loads

_builtin_field_re = compile_regex(r"^__[a-z][a-z0-9_]+__$")


class JSON:
    pass


def env_value_valid(val):
    return val != None and val != ""


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
                    v = varval.lower() != "false" and varval != "0"
            elif field_type == Optional[JSON]:
                optional = True
                if env_value_valid(varval):
                    v = json_loads(varval)
            else:
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
                            v = list(map(lambda x: typ(x.strip()), varval.split(",")))
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
                elif field_type == JSON:
                    v = json_loads(varval)
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
