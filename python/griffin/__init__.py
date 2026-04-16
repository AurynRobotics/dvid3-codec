"""Griffin — fast lossless image codec.

Portable WebAssembly build: runs on any OS/arch supported by wasmtime-py
(Linux, macOS, Windows; x86_64, aarch64). No AVX2 requirement.

Quick start:

    import griffin
    import numpy as np
    from PIL import Image

    img = np.array(Image.open("photo.png").convert("RGBA"))

    encoded = griffin.encode(img)               # fast level (default)
    decoded = griffin.decode(encoded)

    assert np.array_equal(img, decoded)

    # Timed variants for benchmarking:
    encoded, enc_seconds = griffin.encode_timed(img)
    decoded, dec_seconds = griffin.decode_timed(encoded)
"""

from ._runtime import decode as _decode_timed
from ._runtime import encode as _encode_timed

__version__ = "0.2.0"
__all__ = ["encode", "decode", "encode_timed", "decode_timed"]


def encode(img_rgba, level=0):
    """Encode an (H, W, 4) uint8 numpy RGBA array to Griffin bytes.

    Args:
        img_rgba: numpy.ndarray of shape (H, W, 4), dtype uint8.
        level: 0 = fast (default), 1 = best compression.

    Returns:
        bytes — the Griffin-encoded payload.
    """
    data, _ = _encode_timed(img_rgba, level=level)
    return data


def decode(data):
    """Decode Griffin bytes to an (H, W, 4) uint8 numpy RGBA array.

    Args:
        data: bytes, bytearray, or memoryview containing a Griffin file.

    Returns:
        numpy.ndarray of shape (H, W, 4), dtype uint8.
    """
    arr, _ = _decode_timed(data)
    return arr


def encode_timed(img_rgba, level=0):
    """Like `encode`, but also returns the native codec time (seconds).

    Returns:
        (bytes, float) — encoded payload and seconds spent in the codec
        (excludes wasm instance setup + memory copies).
    """
    return _encode_timed(img_rgba, level=level)


def decode_timed(data):
    """Like `decode`, but also returns the native codec time (seconds).

    Returns:
        (numpy.ndarray, float) — decoded image and seconds spent in the codec.
    """
    return _decode_timed(data)
