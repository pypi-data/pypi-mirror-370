from typing import Any, Union

import json
import pickle

try:
    from blissdata.settings import OrderedHashObjSetting
except ImportError:
    try:
        from bliss.config.settings import OrderedHashObjSetting
    except ImportError:
        OrderedHashObjSetting = None


class PersistentOrderedDict(OrderedHashObjSetting):
    def __init__(self, redis_key: str, serializer: str = "json"):
        dumps, loads = _SERIALIZERS[serializer]
        super().__init__(
            redis_key, read_type_conversion=loads, write_type_conversion=dumps
        )


def _json_loads(serialized_value: Union[bytes, Any]) -> Any:
    # Called twice on the same data for bliss<2
    if isinstance(serialized_value, bytes):
        try:
            return json.loads(serialized_value)
        except Exception:
            pass
    return serialized_value


def _pickle_loads(serialized_value: Union[bytes, Any]) -> Any:
    # Called twice on the same data for bliss<2
    if isinstance(serialized_value, bytes):
        try:
            return pickle.loads(serialized_value)
        except Exception:
            pass
    return serialized_value


def _json_dumps(python_value: Any) -> str:
    return json.dumps(python_value)


def _pickle_dumps(python_value: Any) -> bytes:
    return pickle.dumps(python_value)


_SERIALIZERS = {
    "json": (_json_dumps, _json_loads),
    "pickle": (_pickle_dumps, _pickle_loads),
}
