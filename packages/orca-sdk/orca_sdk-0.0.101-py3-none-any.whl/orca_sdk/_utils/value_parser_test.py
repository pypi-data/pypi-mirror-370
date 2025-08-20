import numpy as np
from PIL import Image as pil

from .value_parser import decode_value, encode_value


def test_string_parsing():
    encoded = encode_value("hello world")
    assert encoded == "hello world"

    decoded = decode_value(encoded)
    assert decoded == "hello world"


def test_image_parsing():
    img = pil.new("RGB", (10, 10), color="red")
    img.format = "PNG"

    encoded = encode_value(img)
    assert isinstance(encoded, str)
    assert encoded.startswith("data:image/png;base64,")

    decoded = decode_value(encoded)
    assert isinstance(decoded, pil.Image)
    assert decoded.size == img.size


def test_timeseries_parsing():
    timeseries = np.random.rand(20, 3).astype(np.float32)

    encoded = encode_value(timeseries)
    assert isinstance(encoded, str)
    assert encoded.startswith(f"data:numpy/{timeseries.dtype.name};base64,")

    decoded = decode_value(encoded)
    assert isinstance(decoded, np.ndarray)
    assert decoded.shape == timeseries.shape
    assert decoded.dtype == timeseries.dtype
    assert np.allclose(decoded, timeseries)
