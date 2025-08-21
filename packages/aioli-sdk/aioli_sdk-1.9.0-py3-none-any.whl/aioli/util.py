# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import datetime
import enum
import json
import math
import numbers
import uuid
from typing import Any, Optional, SupportsFloat, cast


def json_encode(obj: Any, indent: Optional[str] = None, sort_keys: bool = False) -> str:
    """
    Encode things as json, with an extra preprocessing step to handle some non-standard types.

    Note: json has a "default" argument that accepts something like our preprocessing step,
    except it is only invoked for non-native types (i.e. no catching nan or inf floats).
    """
    import numpy as np

    def jsonable(obj: Any) -> Any:
        if isinstance(obj, (str, bool, type(None))):
            # Needs no fancy encoding.
            return obj
        if isinstance(obj, numbers.Integral):
            # int, np.int64, etc.
            return int(obj)
        if isinstance(obj, numbers.Number):
            obj = cast(SupportsFloat, obj)
            # float, np.float64, etc.  Serialize nan/±infinity as strings.
            if math.isnan(obj):
                return "NaN"
            if math.isinf(obj):
                return "Infinity" if float(obj) > 0.0 else "-Infinity"
            return float(obj)
        if isinstance(obj, bytes):
            # Assume bytes are utf8 (json can't encode arbitrary binary data).
            return obj.decode("utf8")
        if isinstance(obj, (list, tuple)):
            # Recurse into lists.
            return [jsonable(v) for v in obj]
        if isinstance(obj, dict):
            # Recurse into dicts.
            return {k: jsonable(v) for k, v in obj.items()}
        if isinstance(obj, np.ndarray):
            # Expand arrays into lists, then recurse.
            return jsonable(obj.tolist())
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, uuid.UUID):
            return str(obj)
        # Objects that provide their own custom JSON serialization.
        if hasattr(obj, "__json__"):
            return obj.__json__()
        raise TypeError("Unserializable object {} of type {}".format(obj, type(obj)))

    return json.dumps(jsonable(obj), indent=indent, sort_keys=sort_keys)
