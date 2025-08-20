import base64
import io
from typing import cast

import numpy as np
from numpy.typing import NDArray
from PIL import Image as pil

ValueType = str | pil.Image | NDArray[np.float32]
"""
The type of a value in a memoryset

- `str`: string
- `pil.Image`: image
- `NDArray[np.float32]`: univariate or multivariate timeseries
"""


def decode_value(value: str) -> ValueType:
    if value.startswith("data:image"):
        header, data = value.split(",", 1)
        return pil.open(io.BytesIO(base64.b64decode(data)))

    if value.startswith("data:numpy"):
        header, data = value.split(",", 1)
        return np.load(io.BytesIO(base64.b64decode(data)))

    return value


def encode_value(value: ValueType) -> str:
    if isinstance(value, pil.Image):
        header = f"data:image/{value.format.lower()};base64," if value.format else "data:image;base64,"
        buffer = io.BytesIO()
        value.save(buffer, format=value.format)
        bytes = buffer.getvalue()
        return header + base64.b64encode(bytes).decode("utf-8")

    if isinstance(value, np.ndarray):
        header = f"data:numpy/{value.dtype.name};base64,"
        buffer = io.BytesIO()
        np.save(buffer, value)
        return header + base64.b64encode(buffer.getvalue()).decode("utf-8")

    return value
