"""Internal: wasmtime-py loader and call helpers for libgriffin.wasm."""

import importlib.resources as _res
import struct
import threading

import numpy as np
from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig


_cfg = Config()
_cfg.wasm_relaxed_simd = True
_cfg.wasm_simd = True
_cfg.cache = True
_engine = Engine(_cfg)

# Load the wasm once at import time.
with _res.files("griffin").joinpath("libgriffin.wasm").open("rb") as _f:
    _module = Module(_engine, _f.read())

# Global linker with WASI support.
_linker = Linker(_engine)
_linker.define_wasi()


class _Instance:
    """Wraps one wasmtime instance. Not thread-safe (wasmtime Store is per-thread)."""

    __slots__ = ("store", "inst", "memory", "malloc", "free",
                 "encode_max_size", "encode_level_timed", "read_header", "decode_timed")

    def __init__(self):
        self.store = Store(_engine)
        self.store.set_wasi(WasiConfig())
        self.inst = _linker.instantiate(self.store, _module)
        exports = self.inst.exports(self.store)
        # Reactor modules require an explicit _initialize call before first export use.
        exports["_initialize"](self.store)
        self.memory = exports["memory"]
        self.malloc = exports["malloc"]
        self.free = exports["free"]
        self.encode_max_size = exports["griffin_encode_max_size"]
        self.encode_level_timed = exports["griffin_encode_level_timed"]
        self.read_header = exports["griffin_read_header"]
        self.decode_timed = exports["griffin_decode_timed"]

    def mem_write(self, offset, data):
        self.memory.write(self.store, data, offset)

    def mem_read(self, offset, size):
        return bytes(self.memory.read(self.store, offset, offset + size))

    def read_double(self, ptr):
        return struct.unpack("<d", self.mem_read(ptr, 8))[0]

    def read_int32(self, ptr):
        return struct.unpack("<i", self.mem_read(ptr, 4))[0]


# Thread-local reused instance. wasmtime Store is per-thread; reusing it
# amortizes the ~5ms instance setup cost across calls in the same thread.
_tls = threading.local()


def _get_instance():
    inst = getattr(_tls, "inst", None)
    if inst is None:
        inst = _Instance()
        _tls.inst = inst
    return inst


def _as_rgba(img):
    """Accept (H,W,4) uint8 numpy arrays. Cheap conversions allowed; expensive ones rejected."""
    if not isinstance(img, np.ndarray):
        raise TypeError(f"expected numpy.ndarray, got {type(img).__name__}")
    if img.dtype != np.uint8:
        raise TypeError(f"expected uint8 array, got dtype={img.dtype}")
    if img.ndim != 3 or img.shape[2] != 4:
        raise ValueError(f"expected shape (H, W, 4), got {img.shape}")
    if not img.flags["C_CONTIGUOUS"]:
        img = np.ascontiguousarray(img)
    return img


def encode(img_rgba, level=0):
    """Encode an (H,W,4) uint8 numpy array to Griffin bytes.

    level: 0=auto (default), 1=fast, 2=best.
    """
    img = _as_rgba(img_rgba)
    h, w = img.shape[:2]
    raw_size = w * h * 4

    inst = _get_instance()
    in_ptr = inst.malloc(inst.store, raw_size)
    out_cap = inst.encode_max_size(inst.store, w, h)
    out_ptr = inst.malloc(inst.store, out_cap)
    time_ptr = inst.malloc(inst.store, 8)
    try:
        inst.mem_write(in_ptr, img.tobytes())
        enc_size = inst.encode_level_timed(
            inst.store, in_ptr, w, h, out_ptr, out_cap, int(level), time_ptr
        )
        if enc_size <= 0:
            raise RuntimeError(f"griffin_encode returned {enc_size}")
        return inst.mem_read(out_ptr, enc_size), inst.read_double(time_ptr)
    finally:
        inst.free(inst.store, in_ptr)
        inst.free(inst.store, out_ptr)
        inst.free(inst.store, time_ptr)


def decode(data):
    """Decode Griffin bytes to an (H,W,4) uint8 numpy array."""
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"expected bytes-like, got {type(data).__name__}")
    data = bytes(data)
    enc_size = len(data)
    if enc_size < 18:
        raise ValueError("not a griffin file: too short")

    inst = _get_instance()
    in_ptr = inst.malloc(inst.store, enc_size)
    w_ptr = inst.malloc(inst.store, 4)
    h_ptr = inst.malloc(inst.store, 4)
    time_ptr = inst.malloc(inst.store, 8)
    try:
        inst.mem_write(in_ptr, data)
        if not inst.read_header(inst.store, in_ptr, enc_size, w_ptr, h_ptr):
            raise ValueError("not a griffin file")
        w = inst.read_int32(w_ptr)
        h = inst.read_int32(h_ptr)
        raw_size = w * h * 4

        out_ptr = inst.malloc(inst.store, raw_size)
        try:
            dec_size = inst.decode_timed(inst.store, in_ptr, enc_size, out_ptr, raw_size, time_ptr)
            if dec_size != raw_size:
                raise RuntimeError(f"griffin_decode returned {dec_size}, expected {raw_size}")
            raw = inst.mem_read(out_ptr, raw_size)
            arr = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4).copy()
            return arr, inst.read_double(time_ptr)
        finally:
            inst.free(inst.store, out_ptr)
    finally:
        inst.free(inst.store, in_ptr)
        inst.free(inst.store, w_ptr)
        inst.free(inst.store, h_ptr)
        inst.free(inst.store, time_ptr)
