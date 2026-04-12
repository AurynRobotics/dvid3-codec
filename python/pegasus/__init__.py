"""Pegasus — fast lossless image codec with SIMD preprocessing + LZ4."""

from ._pegasus import decode, decode_timed, encode, encode_timed

__version__ = "0.1.0"
__all__ = ["encode", "decode", "encode_timed", "decode_timed"]
