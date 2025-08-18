use pyo3::{prelude::*, exceptions};
use safetensors::SafeTensors;

use crate::diff::{self, TensorDiff};
use crate::tensor_patch::{TensorPatchFile, TensorPatch};
use safetensors::Dtype;
use std::fs::File;
use std::path::Path;

mod io {
    pyo3::import_exception!(io, FileNotFoundError);
}

fn str_to_dtype(s: &str) -> PyResult<Dtype> {
    match s.to_uppercase().as_str() {
        "F32" => Ok(Dtype::F32),
        "F64" => Ok(Dtype::F64),
        "I32" => Ok(Dtype::I32),
        "I64" => Ok(Dtype::I64),
        "U8"  => Ok(Dtype::U8),
        other => Err(exceptions::PyValueError::new_err(format!("Unknown dtype: {}", other))),
    }
}

fn dtype_to_str(d: &Dtype) -> &'static str {
    match d {
        Dtype::F32 => "F32",
        Dtype::F64 => "F64",
        Dtype::I32 => "I32",
        Dtype::I64 => "I64",
        Dtype::U8  => "U8",
        _ => "UNKNOWN",
    }
}

#[pyfunction]
pub fn resolve_diff(path_origin: String, path_dest: String) -> PyResult<TensorDiff> {
    let origin_file = std::fs::read(path_origin).map_err(|e| exceptions::PyIOError::new_err(format!("read origin error: {}", e)))?;
    let origin_res = SafeTensors::deserialize(&origin_file);

    let dest_file = std::fs::read(path_dest).map_err(|e| exceptions::PyIOError::new_err(format!("read dest error: {}", e)))?;
    let dest_res = SafeTensors::deserialize(&dest_file);

    if let (Ok(origin), Ok(dest)) = (origin_res, dest_res) {
        diff::resolve_diff(origin, dest)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("diff error: {}", e)))
    } else {
        Err(io::FileNotFoundError::new_err("issue reading safe tensor files"))
    }
}

#[pyfunction]
pub fn create_patch_file(path: String, origin_hash: String, dest_hash: String) -> PyResult<()> {
    let p = Path::new(&path);
    let file = File::create(p).map_err(|e| exceptions::PyIOError::new_err(format!("create file error: {}", e)))?;
    TensorPatchFile::create(file, origin_hash, dest_hash)
        .map(|_t| ())
        .map_err(|e| exceptions::PyIOError::new_err(format!("create patch file error: {}", e)))
}

#[pyfunction]
pub fn write_patch_atomic(path: String, name: String, dtype: String, shape: Vec<usize>, data: Vec<u8>, is_delta: bool) -> PyResult<()> {
    let p = Path::new(&path);
    let file = File::options().read(true).write(true).open(p).map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let mut tpf = TensorPatchFile::open(file).map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;

    let dtype_enum = str_to_dtype(&dtype)?;
    let patch = TensorPatch {
        dtype: dtype_enum,
        shape,
        data_offset: 0,
        data_len: data.len() as u64,
        is_delta,
    };

    tpf.write_patch_atomic_with_path(p, &name, patch, &data)
        .map_err(|e| exceptions::PyIOError::new_err(format!("atomic write error: {}", e)))
}

#[pyfunction]
pub fn read_patch(path: String, name: String) -> PyResult<(String, Vec<usize>, Vec<u8>, bool)> {
    let p = Path::new(&path);
    let file = File::open(p).map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let mut tpf = TensorPatchFile::open(file).map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    let (patch, data) = tpf.read_patch(&name).map_err(|e| exceptions::PyIOError::new_err(format!("read patch error: {}", e)))?;
    let dtype_s = dtype_to_str(&patch.dtype).to_string();
    Ok((dtype_s, patch.shape, data, patch.is_delta))
}

#[pyfunction]
pub fn available_patches(path: String) -> PyResult<Vec<String>> {
    let p = Path::new(&path);
    let file = File::open(p).map_err(|e| exceptions::PyIOError::new_err(format!("open file error: {}", e)))?;
    let tpf = TensorPatchFile::open(file).map_err(|e| exceptions::PyIOError::new_err(format!("open patch file error: {}", e)))?;
    Ok(tpf.available_patches())
}

pub(crate) fn register_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(resolve_diff, m)?)?;
    m.add_function(wrap_pyfunction!(create_patch_file, m)?)?;
    m.add_function(wrap_pyfunction!(write_patch_atomic, m)?)?;
    m.add_function(wrap_pyfunction!(read_patch, m)?)?;
    m.add_function(wrap_pyfunction!(available_patches, m)?)?;
    m.add_function(wrap_pyfunction!(resolve_diff_and_write_patch, m)?)?;
    m.add_class::<TensorDiff>()?;
    Ok(())
}

#[pyfunction]
pub fn resolve_diff_and_write_patch(path_origin: String, path_dest: String, out_patch: String) -> PyResult<()> {
    let origin_file = std::fs::read(&path_origin).map_err(|e| exceptions::PyIOError::new_err(format!("read origin error: {}", e)))?;
    let origin_res = SafeTensors::deserialize(&origin_file).map_err(|e| exceptions::PyRuntimeError::new_err(format!("origin deserialize: {}", e)))?;

    let dest_file = std::fs::read(&path_dest).map_err(|e| exceptions::PyIOError::new_err(format!("read dest error: {}", e)))?;
    let dest_res = SafeTensors::deserialize(&dest_file).map_err(|e| exceptions::PyRuntimeError::new_err(format!("dest deserialize: {}", e)))?;

    let out_path = std::path::Path::new(&out_patch);
    crate::diff::resolve_diff_and_write_patch(origin_res, dest_res, out_path)
        .map(|_d| ())
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("resolve/write patch failed: {}", e)))
}
