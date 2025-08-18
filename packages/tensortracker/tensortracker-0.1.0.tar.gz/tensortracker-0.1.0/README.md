# TensorTrack
 
[![PyPI](https://img.shields.io/pypi/v/tensortracker.svg)](https://pypi.org/project/tensortracker/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?logo=apache)](LICENSE)
[![Build Status](https://github.com/james-a-page/tensor-track/workflows/CI/badge.svg)](https://github.com/james-a-page/tensor-track/actions)

TensorTrack is a Rust-first library and prototype tool for computing compact patches between machine-learning model weight files stored in the SafeTensors format. The project provides a Rust core and a PyO3-based Python extension used by small integration tests and benchmarks.

## Features (current)

- Compute diffs between SafeTensors files and write patch files.
- Python bindings exposing convenience helpers (for example, `resolve_diff_and_write_patch`).
- Atomic write path for file-backed patch creation (temporary file + atomic rename).

## Status

This repository is under active development. The Python package is not necessarily published to PyPI from this source; to use the Python API locally, build the extension with `maturin develop -r` or install the package into your environment with `pip`.

## Installation (developer)

Prerequisites:
- Rust (stable toolchain)
- Python 3.9+
- maturin (to build the Python extension)

Build and run Rust tests:

```bash
cargo test
```

Build and install the Python extension locally:

```bash
maturin develop -r
# or
python -m pip install .
```

Run Python tests (some tests skip when optional deps are missing):

```bash
pytest tests/python -q
```

Run the torchvision snapshot benchmark (may skip if torch not installed):

```bash
pytest benchmarks/test_patch_torchvision_benchmark.py -q
```

Benchmark CSV/PNG outputs are placed under `benchmarks/benchmark_outputs/vision/` when run.

## Quick examples

High-level: create a patch between two safetensors files using the Python binding:

```python
import tensortracker

# writes a patch file that encodes changes from origin -> dest
tensortracker.resolve_diff_and_write_patch('origin.safetensors', 'dest.safetensors', 'out.patch')
```

Low-level: the Python extension also exposes read/write helpers for individual patch entries (see `src/python.rs` for exact names and semantics).


## Contributing

See `CONTRIBUTING.md` for developer setup and contribution guidance. In short:

- Run `cargo test` and `pytest` locally before opening PRs.
- Use `maturin develop -r` to iterate on the Python extension.
- Add unit tests for Rust changes and pytest tests for Python-facing behavior.

## License

This project is released under the terms documented in `LICENSE`.

## Citation

If you use this software in research, please reference the repository.

---

If you want, I can also:
- Add a short `benchmarks/README.md` with exact commands and expected CSV/PNG paths; or
- Add a CI workflow stub that builds the extension and runs the benchmark and uploads CSV/PNG artifacts.