"""Chimera — fast lossless image codec producing valid PNG output."""

from ._chimera import decode, decode_timed, encode, encode_timed

__version__ = "0.1.0"
__all__ = ["encode", "decode", "encode_timed", "decode_timed"]
