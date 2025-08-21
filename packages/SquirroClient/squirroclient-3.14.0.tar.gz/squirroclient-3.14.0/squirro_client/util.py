import datetime
import time
import warnings
from numbers import Number
from typing import Any, Callable, Optional, Union


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


# Enable deprecation warnings.
warnings.simplefilter("default")


def _clean_params(params: dict[str, Optional[Any]]) -> dict[str, Any]:
    """Remove params without value"""
    return {param: value for param, value in params.items() if value is not None}


def _json_default(o):
    """
    Somewhat ujson-compatible with serialization default.

    Based on squirro.common.format.JsonSerialization._default
    """
    if isinstance(o, bytes):
        return o.decode("utf-8")
    if isinstance(o, Number):
        return float(o)
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    if isinstance(o, time.struct_time):
        return time.strftime("%Y-%m-%dT%H:%M:%S", o)
    raise TypeError(f"Object of type {type(o)} is not JSON serializable {str(o)[:100]}")


try:
    import orjson
except ImportError:
    import json as _json

    def _loads(s: Union[str, bytes]) -> Any:
        return _json.loads(s)

    def _dumps(obj) -> str:
        return _json.dumps(obj, default=_json_default)

else:

    def _loads(s: Union[str, bytes]) -> Any:
        """Speedier JSON deserialization."""
        return orjson.loads(s)

    def _dumps(obj) -> bytes:
        """Speedier JSON serialization."""
        return orjson.dumps(
            obj,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=_json_default,
        )


_loads: Callable[[Union[str, bytes]], Any]
_dumps: Callable[[Any], Union[str, bytes]]
