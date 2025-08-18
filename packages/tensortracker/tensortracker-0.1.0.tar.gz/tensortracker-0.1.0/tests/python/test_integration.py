import pytest
import tempfile
import os
import struct

try:
    import tensortrack
except Exception as e:
    pytest.skip("tensortrack python extension not installed. Build with: `maturin develop -r` or `python -m pip install .`", allow_module_level=True)


def test_high_level_resolve_diff(tmp_path):
    """
    High-level test: create two safetensors (with torch if available), modify one,
    and call resolve_diff to get the TensorDiff. Falls back to low-level patch-file
    test if safetensors/torch aren't available.
    """
    # Prefer torch+safetensors path
    try:
        import torch
        from safetensors.torch import save_file
        has_torch = True
    except Exception:
        has_torch = False

    if has_torch:
        # Create tensors
        a = torch.tensor([[0.0, 1.0, 12.2, 42.5, 2132.4], [2.0, 3.0, 12.2, 42.5, 2132.4]], dtype=torch.float32)
        b = torch.tensor([[0.0, 1.5, 12.2, 42.5, 214.1], [2.0, 3.5, 12.2, 42.5, 1.4]], dtype=torch.float32)

        origin_path = str(tmp_path / "origin.safetensors")
        dest_path = str(tmp_path / "dest.safetensors")
        patch_path = str(tmp_path / "out.patch")

        save_file({"test_layer": a}, origin_path)
        save_file({"test_layer": b}, dest_path)
        # Create patch file on disk using high-level API
        tensortrack.resolve_diff_and_write_patch(origin_path, dest_path, patch_path)

        # Reconstruct dest by applying patches: load origin, then overwrite changed tensors
        from safetensors.torch import load_file

        origin = load_file(origin_path)
        # Read patches from patch file
        patches = tensortrack.available_patches(patch_path)
        assert "test_layer" in patches
        dtype_s, shape, data, is_delta = tensortrack.read_patch(patch_path, "test_layer")
        data_bytes = bytes(data)

        # Convert data_bytes into a torch tensor with correct dtype
        import numpy as np
        arr = np.frombuffer(data_bytes, dtype=np.float32)
        arr = arr.reshape(tuple(shape))
        import torch
        reconstructed = {"test_layer": torch.from_numpy(arr.copy())}
        print(reconstructed)

        # Save reconstructed tensor and compare bytewise to dest file
        reconstructed_path = str(tmp_path / "reconstructed.safetensors")
        save_file(reconstructed, reconstructed_path)

        # Print sizes for inspection (patch may be larger for small tensors)
        patch_size = os.path.getsize(patch_path)
        dest_size = os.path.getsize(dest_path)
        rec_size = os.path.getsize(reconstructed_path)
        print(f"sizes: patch={patch_size}, dest={dest_size}, recon={rec_size}")

        with open(dest_path, "rb") as f:
            dest_bytes = f.read()
        with open(reconstructed_path, "rb") as f:
            rec_bytes = f.read()

        # Ensure reconstruction equals the destination
        assert dest_bytes == rec_bytes
        assert dest_bytes == rec_bytes
    else:
        # Fallback: verify low-level file API if present
        p = tmp_path / "test.patch"
        path = str(p)

        # Create patch file
        tensortrack.create_patch_file(path, "origin123", "dest456")

        # Prepare data: four float32 values
        data = struct.pack("4f", 0.0, 1.0, 2.0, 3.0)

        # Write patch atomically
        try:
            tensortrack.write_patch_atomic(path, "layer1", "F32", [2, 2], data, True)
        except Exception:
            pytest.skip("low-level write/read API not available")

        # Check available patches
        patches = tensortrack.available_patches(path)
        assert "layer1" in patches

        # Read back the patch
        dtype_str, shape, read_data, is_delta = tensortrack.read_patch(path, "layer1")
        assert dtype_str == "F32"
        assert shape == [2, 2]
        assert read_data == data
        assert is_delta is True
