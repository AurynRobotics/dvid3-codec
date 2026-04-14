# Griffin

Fast lossless image codec that compresses better than PNG.

Griffin automatically adapts its compression strategy to the image content — using Huffman entropy coding for photographic images and dictionary compression for text/document images. No manual tuning needed.

**Portable by default.** This distribution ships as a single WebAssembly binary that runs on **any OS/arch**: Linux, macOS, Windows; x86_64, aarch64. No CPU feature requirements, no per-platform builds.

---

## Quick start

Clone this repo once — both the CLI and the Python package live inside it:

```bash
git clone https://github.com/AurynRobotics/dvid3-codec.git
cd dvid3-codec
```

### 60-second install — Python

```bash
pip install -e .
```

```python
import griffin
import numpy as np
from PIL import Image

img = np.array(Image.open("photo.png").convert("RGBA"))
encoded = griffin.encode(img)
decoded = griffin.decode(encoded)
```

Works on any Python 3.9+ on Linux, macOS, Windows. `wasmtime` and `numpy` are
pulled in automatically as dependencies.

### 60-second install — CLI

```bash
# 1. Install the wasm runtime (one-shot, no sudo; Linux / macOS / WSL)
bash bin/install-wasmtime.sh

# 2. Encode / decode
bin/dvid3 encode --in photo.png --out photo.grif
bin/dvid3 decode --in photo.grif --out photo.png
```

On Windows use `bin\dvid3.cmd` and install wasmtime via:
```powershell
powershell -Command "iwr https://wasmtime.dev/install.ps1 -useb | iex"
```

---

## CLI — full reference

```bash
# Single file
bin/dvid3 encode --in image.png   --out image.grif
bin/dvid3 decode --in image.grif  --out image.png

# Compression levels: auto (default), fast, best
bin/dvid3 encode --level best --in photo.png --out photo.grif

# Batch — directories with CSV report
bin/dvid3 encode --in images/  --out encoded/  --report encode.csv
bin/dvid3 decode --in encoded/ --out decoded/  --report decode.csv
```

The CSV report contains per-file size, ratio, and codec time (MiB/s). Paths can be relative or absolute; the launcher handles wasm sandboxing automatically.

---

## Python — full API

```python
import griffin
import numpy as np
from PIL import Image

img = np.array(Image.open("photo.png").convert("RGBA"))

# Basic encode/decode
encoded = griffin.encode(img)                 # bytes
decoded = griffin.decode(encoded)             # (H, W, 4) uint8 ndarray

# Explicit compression level
encoded = griffin.encode(img, level=2)        # 0=auto, 1=fast, 2=best

# Timed variants — returns (result, seconds_in_codec) for benchmarking
encoded, enc_s = griffin.encode_timed(img)
decoded, dec_s = griffin.decode_timed(encoded)
```

Input must be an `(H, W, 4)` uint8 numpy array. Use PIL's `.convert("RGBA")` if your source is RGB.

### Benchmark your own images

```bash
python bench_codecs.py images/tecnick/
```

(`bench_codecs.py` lives next to this README. `pip install pillow numpy` first if you don't have them.)

---

## Benchmarks

All speeds are raw pixel throughput (width × height × channels / time), single core, best-of-3 iterations. Ratio is encoded size / uncompressed size using the original channel count.

**Methodology:** Single core (Intel Core i7-13700H P-core), sequential execution, pre-allocated buffers and reusable contexts. WebP lossless uses method=0/quality=0 (fastest). JPEG-XL lossless uses effort=3.

> ### Note on benchmarks and the WebAssembly distribution
>
> **The numbers above were measured with the native AVX2 build** of Griffin
> (`-march=haswell`, no wasm runtime). They reflect the codec's raw algorithmic
> performance on bare metal.
>
> **This distribution ships a WebAssembly build, not the native binary.** We
> made that choice deliberately:
>
> 1. **Portability** — a single `.wasm` artifact runs on Linux, macOS, Windows
>    and on x86_64, aarch64, riscv64 alike. No per-platform builds, no AVX2
>    requirement, no install friction.
> 2. **Strong sandboxing** — WebAssembly executes in an isolated memory space
>    with no access to arbitrary syscalls, the network, or files outside the
>    directories you explicitly grant. A malicious or buggy codec can't read
>    your SSH keys, write to `~`, or exfiltrate anything. You can run untrusted
>    `.grif` inputs through it with meaningful safety guarantees — something
>    the native binary cannot offer.
>
> **Benchmarking the wasm build will show lower throughput than the numbers
> above.** Two reasons:
>
> - WebAssembly SIMD is capped at 128-bit vectors; the native Griffin code uses
>   256-bit AVX2. The wasm runtime recovers much of that ground with JIT
>   tuning to the exact host CPU, but doesn't fully close the gap.
> - Calling the codec from Python (via `wasmtime-py`) adds per-call FFI
>   overhead for argument marshalling and memory copies in/out of the wasm
>   linear memory.
>
> Expect the wasm CLI to land within ~10% of the native numbers in your own
> measurements, and the Python path around 20–30% lower than native. Ratios
> (compression effectiveness) are identical — the algorithm is unchanged.

### Tecnick dataset (182 photographic images, 1200x1200 RGB)

![Tecnick benchmark](bench_tecnick.png)

### DocBank dataset (200 document pages, ~770x1000 RGB)

![DocBank benchmark](bench_docbank.png)

### Datasets

- **Tecnick** — 182 photographic images at 1200x1200 from the [Tecnick SAMPLING dataset](https://sourceforge.net/projects/testimages/files/SAMPLING_8BIT_RGB_1200x1200.tar.bz2/download). The standard benchmark for lossless image codec evaluation.
- **DocBank** — 200 document page images from the [DocBank dataset](https://doc-analysis.github.io/docbank-page/). Academic papers rendered to PNG.

```bash
# Tecnick (182 images, ~370 MB)
curl -L "https://sourceforge.net/projects/testimages/files/SAMPLING_8BIT_RGB_1200x1200.tar.bz2/download" -o tecnick.tar.bz2
mkdir -p images/tecnick
tar xjf tecnick.tar.bz2 -C images/tecnick
rm tecnick.tar.bz2
```

---

## What's in this directory

| Path | Purpose |
|---|---|
| `bin/dvid3` | POSIX CLI launcher (bash) |
| `bin/dvid3.cmd` | Windows CLI launcher |
| `bin/dvid3.wasm` | Griffin codec CLI, portable WebAssembly |
| `bin/install-wasmtime.sh` | Helper: installs wasmtime to `~/.wasmtime/bin` |
| `bin/libgriffin.a` + `bin/griffin.h` | C static library (Linux x86_64, for embedders) |
| `python/griffin/` | Python package (uses `wasmtime-py` + `libgriffin.wasm`) |
| `bench_codecs.py` | Python benchmark runner |
| `images/` | Sample images for quick testing |

---

## Runtime requirements

### Python path
- **Python 3.9+** (any OS, any CPU arch)
- `pip install -e .` from the cloned repo pulls in `wasmtime` and `numpy` automatically

### CLI path
- Any OS / arch supported by [wasmtime](https://wasmtime.dev) (Linux, macOS, Windows; x86_64, aarch64)
- `bin/install-wasmtime.sh` installs it in one shot, no sudo, to `~/.wasmtime/`
- Alternatively install via your package manager: `brew install wasmtime`, `apt install wasmtime` (where available), or [the one-line installer](https://wasmtime.dev)

**No AVX2 requirement.** The wasm runtime JITs to whatever your CPU supports.

---

## C static library (optional, for embedders)

`bin/libgriffin.a` + `bin/griffin.h` — native Linux x86_64 build for programs that want to link Griffin directly without the wasm indirection.

```c
#include "griffin.h"

int cap = griffin_encode_max_size(w, h);
uint8_t* out = malloc(cap);
int enc_size = griffin_encode_level(pixels, w, h, out, cap, GRIFFIN_BEST);

double seconds;
int enc_size = griffin_encode_timed(pixels, w, h, out, cap, &seconds);
```

```bash
gcc -I bin/ my_app.c bin/libgriffin.a -lstdc++ -lpthread -o my_app
```

For portability across OS/arch, prefer the Python package or the CLI.

---

## Troubleshooting

### `error: wasmtime not found`
Run `bash bin/install-wasmtime.sh` (or on Windows, use the PowerShell install line above). After install, either open a fresh shell or run:
```bash
export PATH="$HOME/.wasmtime/bin:$PATH"
```

### `ModuleNotFoundError: No module named 'wasmtime'` (Python)
You forgot to install the package. From the cloned repo root: `pip install -e .`
(or install the runtime deps directly: `pip install wasmtime numpy`).

### Slow first call in Python
The first `griffin.encode(...)` or `griffin.decode(...)` call pays a ~5 ms one-time cost to instantiate the wasm module. Subsequent calls reuse the instance and are full-speed.

### `can't fopen` on CLI
Your file path may not be inside a preopened directory. The launcher automatically grants access to `$(pwd)` and to the parent dirs of `--in`/`--out`/`--report` arguments; just avoid passing paths that cross symlinks outside of those.

---

## License

Released for **non-commercial evaluation only**. No warranty. See [LICENSE](LICENSE) for details.

This software uses third-party libraries under their respective open-source licenses. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for full license texts.

For commercial licensing: dfaconti@aurynrobotics.com
