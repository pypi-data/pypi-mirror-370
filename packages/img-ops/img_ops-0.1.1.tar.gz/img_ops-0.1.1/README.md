# ImageOperations

**ImageOperations** is a minimal, device‑aware image ops library built on top of OpenCV and NumPy.
You can call functions directly **without initialization**, or use a small facade class with a
**default device** (CPU/GPU/MPS placeholder). When the requested device is unavailable, the library
**transparently falls back to CPU**.

- ✅ Functional API *and* OOP API
- ✅ Device selection per call (`device="cpu"|"gpu"|"mps"`)
- ✅ Safe fallback (GPU/MPS → CPU)
- ✅ Typed (PEP 561, `py.typed`)
- ✅ Clean, modular structure (`ops/`, `registry`, `device`, `types`)
- 🔧 Easy to extend: add new ops or backends without touching the public API

> **Note:** MPS (Apple Metal) is reserved in `ComputeDevice` but currently falls back to CPU.

---

## Installation

```bash
poetry add img-ops
# or with pip:
# pip install img-ops
```

**Headless environments:** replace `opencv-python` with `opencv-python-headless` in your environment
if you don't need GUI capabilities.

---

## Quick Start

### Functional API

```python
from img_ops import bgr_to_hsv, in_range, gauss_blur, ComputeDevice

hsv = bgr_to_hsv(img, device="gpu")  # uses GPU if CUDA available; else CPU
mask = in_range(hsv, (0, 80, 80), (10, 255, 255))  # default device (CPU)
blur = gauss_blur(img, (5, 5), 1.2, device=ComputeDevice.CPU)
```

### OOP API with default device

```python
from img_ops import ImageProcessor

proc = ImageProcessor(default_device="gpu")
hsv = proc.bgr_to_hsv(img)  # defaults to GPU (fallback → CPU)
mask = proc.in_range(hsv, (0, 80, 80), (10, 255, 255))  # uses proc.default_device
blur = proc.gauss_blur(img, (5, 5), 1.2, device="cpu")  # per-call override → CPU
```

---

## Supported Operations (initial set)

- **Color**: `bgr_to_rgb`, `bgr_to_hsv`, `in_range`
- **Filters**: `gauss_blur`
- **Segmentation (CPU-only)**: `find_contours`, `connected_components`
- **Utils**: `sum_masks` (internal registry op)

Add more ops by editing `registry.py` and adding thin wrappers in `ops/`.

---

## Devices

```python
from img_ops import ComputeDevice
# ComputeDevice.GPU  -> CUDA (if available)
# ComputeDevice.MPS  -> reserved (falls back to CPU)
# ComputeDevice.CPU  -> always available
```

### Fallback behavior
- If you request `GPU` and CUDA is unavailable, the call automatically falls back to `CPU`.
- `MPS` is a placeholder and currently always falls back to `CPU`.

---

## Types

The library ships with type hints and `py.typed`.

```python
from img_ops import CvImage, PointHSV

# CvImage: NDArray[uint8 | float32]  # shape (H,W,3) or (H,W)
# PointHSV: tuple[int, int, int]     # (H, S, V)
```

Shape is not fixed in the type system; keep (H, W) or (H, W, 3) by convention.

---

## Error Handling

- Unknown device strings raise `ValueError` with allowed values.
- Missing implementations raise `NotImplementedError` (after attempting CPU fallback).

---

## Extending the Library

### Add a new operation
1. Implement CPU/GPU/MPS callables in `registry.py` under `_cpu()`, `_gpu()`, `_mps()`.
2. Add a thin function wrapper in `ops/<category>.py` that normalizes `device` and calls `dispatch(...)`.
3. (Optional) Expose it in `ops/__init__.py` and the package `__init__.py`.

### Add a new device
1. Extend `ComputeDevice` (e.g., `OPENCL`, `TORCH`).
2. Add a registry builder (e.g., `_opencl()`), wire it in `REGISTRY`.
3. Add availability checks in `device.py` and normalization in each `ops/*.py` wrapper.

This keeps public API stable while evolving internals.

---

## Performance Notes

- GPU helps mostly for larger images or heavy kernels; small images can be faster on CPU due to
  upload/download overhead.
- Prefer `cv2.add` over `a + b` for masks to handle saturation properly.

---

## Testing

```bash
poetry run pytest
poetry run mypy src/img_ops
poetry run ruff check .
```

---
## Author

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/omigutin)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/omigutin)

**Project:** <https://github.com/omigutin/img_ops>

**Project Tracker:** <https://github.com/users/omigutin/projects/4>

**Contact:** [migutin83@yandex.ru](mailto:migutin83@yandex.ru)

---

## License

MIT License.
See [LICENSE](LICENSE) for details.
