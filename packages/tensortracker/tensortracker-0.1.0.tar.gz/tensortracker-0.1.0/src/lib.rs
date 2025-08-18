use pyo3::prelude::*;

pub mod diff;
pub mod tensor_patch;
pub mod compression;
pub mod verification;
mod python;

/// Main Python module
#[pymodule]
fn tensortracker(m: &Bound<'_, PyModule>) -> PyResult<()> {
    python::register_module(m)?;
    Ok(())
}
