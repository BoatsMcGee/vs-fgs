# vs-fgs

A VapourSynth plugin for applying Film Grain Synthesis (FGS) using the [dav1d](https://code.videolan.org/videolan/dav1d) engine.

Since `dav1d` is widely regarded as the best and fastest AV1 decoder available, its FGS engine is fully spec-compliant with **AFGS1** (AOMedia Film Grain Synthesis 1), guaranteeing highly accurate, performant, and standardized grain generation.

`vsfgs` parses standard FGS text files and applies film grain to the input clip natively in **8-bit, 10-bit, or 12-bit YUV**. It also handles automatic dithering if the input bit depth is higher.

## Installation
```bash
pip install vsfgs
```

## Usage

```python
import vapoursynth as vs
import vsfgs

core = vs.core

# 1. Load your video
clip = core.lsmas.LWLibavSource("source.mkv")

# 2. Apply Film Grain
# - ignore_chroma: If True, grain is only applied to Luma (Chroma is copied).
# - static: If True, uses the seed from the FGS table for all frames. If False, rotates the seed for each frame.
clip = vsfgs.apply_fgs(clip, "grain_table.txt", ignore_chroma=False, static=False)

clip.set_output()
```

## Advanced Customization

`vsfgs` allows for extreme and advanced customization of the film grain pattern. The logic for synthesizing grain relies on a detailed parameter table.
For an advanced visual editor to fine-tune these parameters and for more details on the grain configuration, please refer to the **FGSEditor** wiki:
[https://github.com/PingWer/FGSEditor](https://github.com/PingWer/FGSEditor)

## Performance & Compatibility

`vsfgs` uses `dav1d`'s hand-written Assembly instructions (AVX-512, AVX2, SSSE3), resulting in extremely high throughput with almost zero overhead.

**Platform Support:**

| OS | Architecture | Supported | Tested |
| :--- | :--- | :---: | :---: |
| **Windows** | x86_64, ARM64 | ✅ | ✅ |
| **Linux** | x86_64, aarch64 | ✅ | ❌ |
| **macOS** | x86_64, Apple Silicon | ✅ | ❌ |

**Benchmark Comparison** *(1080p 16-bit inputs, FPS)*:
Tests performed using a real MKV source via `vsbestsource` to measure the raw decoding speed, comparing the overhead of `vsfgs` against `Grainer.GAUSS` (from `vsjetpack`).

| Format | Indexer Only | `vsfgs` (AVX-512) | `Grainer.GAUSS` |
| --- | --- | --- | --- |
| **YUV420P16** | ~909 FPS | **~425 FPS** | ~327 FPS |
| **YUV422P16** | - | **~400 FPS** | ~320 FPS |
| **YUV444P16** | - | **~318 FPS** | ~318 FPS |

## Building from Source

To compile the plugin manually, you must have a working C++ toolchain and Meson setup. The plugin depends on `dav1d`, which will be built automatically as a Meson subproject.

### Prerequisites

- **Python 3.13+** (or newer)
- **C++ Compiler**: GCC/Clang (Linux/macOS) or MSVC (Windows)
- **Meson & Ninja**: Build system (`pip install meson ninja`)
- **nasm**: Highly recommended for x86/x64 systems to enable `dav1d` assembly optimizations (drastically improves grain synthesis performance).
  - *Windows*: `choco install nasm`
  - *Linux*: `sudo apt-get install nasm` or `sudo dnf install nasm`
  - *macOS*: `brew install nasm`

### Build Steps

1. Clone the repository recursively to fetch the `dav1d` submodule:
   ```bash
   git clone --recursive https://github.com/your-username/vs-fgs.git
   cd vs-fgs
   ```

2. Build and install the plugin directly into your active Python environment:
   ```bash
   pip install .
   ```
   Upon a successful build, the compiled DLL/SO/DYLIB will be placed in your `site-packages/vapoursynth/plugins` folder, ready for automatic discovery by VapourSynth.

### Standalone Build (Without Python Installation)

If you only want to compile the VapourSynth plugin binary (DLL/SO/DYLIB) without installing it via pip, you can use Meson directly:

```bash
meson setup build --buildtype=release
meson compile -C build
```
## License

This project is licensed under the **MIT License**.
