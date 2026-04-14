#!/usr/bin/env python3
"""Benchmark Griffin codec on a directory of PNG images.

Usage (after `pip install griffin-wasm` or `pip install -e .` from this folder):
    python bench_codecs.py images/kodak/
    python bench_codecs.py images/tecnick/
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

try:
    import griffin
except ImportError:
    print("Griffin module not found. Install with: pip install griffin-wasm", file=sys.stderr)
    print("(or from this repo root: pip install -e .)", file=sys.stderr)
    sys.exit(1)


def bench(paths):
    total_raw = 0
    total_enc = 0
    total_enc_s = 0.0
    total_dec_s = 0.0

    for path in paths:
        orig = Image.open(path)
        channels = len(orig.getbands())
        img = np.array(orig.convert("RGBA"))
        raw = img.shape[0] * img.shape[1] * channels

        encoded, enc_s = griffin.encode_timed(img)
        decoded, dec_s = griffin.decode_timed(encoded)
        assert np.array_equal(decoded, img), f"Round-trip FAILED on {path}"

        ratio = 100.0 * len(encoded) / raw
        enc_mibs = raw / enc_s / (1024 * 1024)
        dec_mibs = raw / dec_s / (1024 * 1024)
        print(f"  {os.path.basename(path):20s}  ratio {ratio:5.1f}%  enc {enc_mibs:7.0f} MiB/s  dec {dec_mibs:7.0f} MiB/s")

        total_raw += raw
        total_enc += len(encoded)
        total_enc_s += enc_s
        total_dec_s += dec_s

    if total_raw > 0:
        n = len(paths)
        print(f"\n  {'TOTAL':20s}  ratio {100.0 * total_enc / total_raw:5.1f}%  enc {total_raw / total_enc_s / (1024**2):7.0f} MiB/s  dec {total_raw / total_dec_s / (1024**2):7.0f} MiB/s")
        print(f"  {n} images, {total_raw / (1024**2):.1f} MiB raw")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Griffin codec")
    parser.add_argument("img_dir", nargs="?", default="images/kodak", help="Directory of PNG images")
    args = parser.parse_args()

    paths = sorted(
        os.path.join(dp, f)
        for dp, _, fns in os.walk(args.img_dir)
        for f in fns
        if f.lower().endswith(".png")
    )
    if not paths:
        print(f"No PNG images found in {args.img_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== GRIFFIN ===\n")
    bench(paths)


if __name__ == "__main__":
    main()
