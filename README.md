# Griffin

Fast lossless image codec that compresses better than PNG.

Griffin automatically adapts its compression strategy to the image content — using Huffman entropy coding for photographic images and dictionary compression for text/document images. No manual tuning needed.

## Benchmarks

All speeds are raw pixel throughput (width x height x channels / time), single core, best-of-3 iterations. Ratio is encoded size / uncompressed size using the original channel count.

**Methodology:** Single core (Intel Core i7-13700H P-core), sequential execution, pre-allocated buffers and reusable contexts. WebP lossless uses method=0/quality=0 (fastest). JPEG-XL lossless uses effort=3.

### Tecnick dataset (182 photographic images, 1200x1200 RGB)

![Tecnick benchmark](bench_tecnick.png)

### DocBank dataset (200 document pages, ~770x1000 RGB)

![DocBank benchmark](bench_docbank.png)

## Datasets

- **Tecnick** — 182 photographic images at 1200x1200 from the [Tecnick SAMPLING dataset](https://sourceforge.net/projects/testimages/files/SAMPLING_8BIT_RGB_1200x1200.tar.bz2/download). The standard benchmark for lossless image codec evaluation.
- **DocBank** — 200 document page images from the [DocBank dataset](https://doc-analysis.github.io/docbank-page/). Academic papers rendered to PNG.

### Downloading datasets

```bash
# Tecnick (182 images, ~370 MB)
curl -L "https://sourceforge.net/projects/testimages/files/SAMPLING_8BIT_RGB_1200x1200.tar.bz2/download" -o tecnick.tar.bz2
mkdir -p images/tecnick
tar xjf tecnick.tar.bz2 -C images/tecnick
rm tecnick.tar.bz2
```

## Independent evaluation

Pre-built binaries are available so the community can independently reproduce and verify these results on their own hardware and datasets.

### AppImage CLI (Linux x86_64)

Single-file executable, no dependencies. Available in the `bin/` directory. Supports single-file and batch (directory) mode with per-file CSV reporting.

```bash
chmod +x bin/dvid3-x86_64.AppImage

# Single file
./bin/dvid3-x86_64.AppImage encode --in photo.png --out photo.grif
./bin/dvid3-x86_64.AppImage decode --in photo.grif --out photo.png

# Compression levels: 0=AUTO (default), 1=FAST, 2=BEST
./bin/dvid3-x86_64.AppImage encode --level 2 --in photo.png --out photo.grif

# Batch encode a directory (recursive), with per-file CSV report
./bin/dvid3-x86_64.AppImage encode --in images/ --out encoded/ --force --report encode.csv

# Batch decode
./bin/dvid3-x86_64.AppImage decode --in encoded/ --out decoded/ --force --report decode.csv
```

Batch mode measures codec time only (excludes PNG load/save I/O), reuses contexts and pre-allocated buffers, and prints aggregate statistics with avg/median/p5/p95 speeds.

### C static library

Pre-built static library and header in the `bin/` directory:

| Library | Header |
|---------|--------|
| `libgriffin.a` | `griffin.h` |

Pure C API, caller owns all memory:

```c
#include "griffin.h"

uint8_t out[griffin_encode_max_size(width, height)];
int encoded_size = griffin_encode(pixels, width, height, out, sizeof(out));

// With explicit compression level
int encoded_size = griffin_encode_level(pixels, width, height, out, sizeof(out), GRIFFIN_BEST);

// Timed variant excludes caller overhead
double seconds;
int encoded_size = griffin_encode_timed(pixels, w, h, out, sizeof(out), &seconds);
```

Compile and link:
```bash
gcc -I bin/ my_benchmark.c bin/libgriffin.a -lstdc++ -lpthread -o my_benchmark
```

### Python (Linux x86_64, Python 3.12+)

Pre-built native module in `python/`. To use:

```bash
pip install numpy pillow   # dependencies
PYTHONPATH=python python bench_codecs.py images/tecnick/
```

The module API:

```python
import griffin
import numpy as np
from PIL import Image

img = np.array(Image.open("photo.png").convert("RGBA"))

encoded = griffin.encode(img)              # AUTO (default)
encoded = griffin.encode(img, level=2)     # BEST
decoded = griffin.decode(encoded)

# Timed variants for benchmarking (measures codec time only)
encoded, enc_seconds = griffin.encode_timed(img)
decoded, dec_seconds = griffin.decode_timed(encoded)
```

## CPU requirements

Griffin requires **AVX2** (Intel Haswell 2013+ / AMD Excavator 2015+). The Python module checks at import time and raises a clear error on unsupported CPUs.

## License

Released for **non-commercial evaluation only**. No warranty. See [LICENSE](LICENSE) for details.

This software uses third-party libraries under their respective open-source licenses. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for full license texts.

For commercial licensing: dfaconti@aurynrobotics.com
