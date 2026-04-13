#!/usr/bin/env python3
"""Benchmark dvid3 codecs on a directory of PNG images.

Usage:
    PYTHONPATH=python python bench_codecs.py images/kodak/
    PYTHONPATH=python python bench_codecs.py images/kodak/ --codec griffin
    PYTHONPATH=python python bench_codecs.py images/kodak/ --codec pegasus
    PYTHONPATH=python python bench_codecs.py images/kodak/ --codec chimera
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

CODECS = {}

try:
    import griffin
    CODECS["griffin"] = griffin
except ImportError:
    pass

try:
    import pegasus
    CODECS["pegasus"] = pegasus
except ImportError:
    pass

try:
    import chimera
    CODECS["chimera"] = chimera
except ImportError:
    pass


def bench_codec(name, codec, paths):
    total_raw = 0
    total_enc = 0
    total_enc_s = 0.0
    total_dec_s = 0.0
    skipped = 0

    for path in paths:
        orig = Image.open(path)
        channels = len(orig.getbands())
        img = np.array(orig.convert("RGBA"))
        raw = img.shape[0] * img.shape[1] * channels

        try:
            encoded, enc_s = codec.encode_timed(img)
        except RuntimeError:
            skipped += 1
            continue

        decoded, dec_s = codec.decode_timed(encoded)
        assert np.array_equal(decoded, img), f"Round-trip FAILED: {name} on {path}"

        ratio = 100.0 * len(encoded) / raw
        enc_mibs = raw / enc_s / (1024 * 1024)
        dec_mibs = raw / dec_s / (1024 * 1024)
        print(f"  {os.path.basename(path):20s}  ratio {ratio:5.1f}%  enc {enc_mibs:7.0f} MiB/s  dec {dec_mibs:7.0f} MiB/s")

        total_raw += raw
        total_enc += len(encoded)
        total_enc_s += enc_s
        total_dec_s += dec_s

    if total_raw > 0:
        n = len(paths) - skipped
        print(f"\n  {'TOTAL':20s}  ratio {100.0 * total_enc / total_raw:5.1f}%  enc {total_raw / total_enc_s / (1024**2):7.0f} MiB/s  dec {total_raw / total_dec_s / (1024**2):7.0f} MiB/s")
        print(f"  {n} images, {total_raw / (1024**2):.1f} MiB raw")
        if skipped:
            print(f"  ({skipped} images skipped)")


def main():
    parser = argparse.ArgumentParser(description="Benchmark dvid3 codecs")
    parser.add_argument("img_dir", nargs="?", default="images/kodak", help="Directory of PNG images")
    parser.add_argument("--codec", choices=list(CODECS.keys()), help="Benchmark only this codec (default: all)")
    args = parser.parse_args()

    if not CODECS:
        print("No codec modules found. Run with: PYTHONPATH=python python bench_codecs.py", file=sys.stderr)
        sys.exit(1)

    paths = sorted(
        os.path.join(dp, f)
        for dp, _, fns in os.walk(args.img_dir)
        for f in fns
        if f.lower().endswith(".png")
    )
    if not paths:
        print(f"No PNG images found in {args.img_dir}", file=sys.stderr)
        sys.exit(1)

    codecs_to_run = {args.codec: CODECS[args.codec]} if args.codec else CODECS

    for name, codec in codecs_to_run.items():
        print(f"\n=== {name.upper()} ===\n")
        bench_codec(name, codec, paths)


if __name__ == "__main__":
    main()
