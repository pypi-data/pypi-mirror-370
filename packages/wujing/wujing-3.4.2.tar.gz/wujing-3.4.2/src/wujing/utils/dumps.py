import json
from typing import Any, Optional

import jsonpickle

jsonpickle.set_encoder_options("json", ensure_ascii=False)


def dumps2json(obj: Any, indent: int = 4, fallback_to_pickle: bool = True) -> Optional[str]:
    if obj is None:
        return json.dumps(None, indent=indent, ensure_ascii=False)

    if not isinstance(indent, int) or indent < 0:
        raise ValueError("indent must be a non-negative integer")

    try:
        result = json.dumps(obj, indent=indent, ensure_ascii=False)
        return result
    except (TypeError, ValueError, OverflowError) as e:
        if not fallback_to_pickle:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable") from e

    try:
        result = jsonpickle.encode(obj, indent=indent)
        return result
    except Exception as e:
        raise TypeError(f"Unable to serialize object of type {type(obj)}: {e}") from e


if __name__ == "__main__":
    print(dumps2json({"nested": {"data": [1, 2, {"deep": "value"}]}}))
