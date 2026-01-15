use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};

pub mod tiff_decoder;
pub mod czi_decoder;
pub mod metadata;
pub mod utils;

use crate::metadata::ImageMetadata;

#[pyclass]
pub struct ZStackDecoder {
    #[pyo3(get)]
    pub supported_formats: Vec<String>,
}

#[pymethods]
impl ZStackDecoder {
    #[new]
    pub fn new() -> Self {
        ZStackDecoder {
            supported_formats: vec![
                "tiff".to_string(),
                "tif".to_string(),
                "czi".to_string(),
                "nd2".to_string(),
                "lsm".to_string(),
            ],
        }
    }

    pub fn decode_file(&self, py: Python, file_path: &str) -> PyResult<PyObject> {
        let extension = std::path::Path::new(file_path)
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("")
            .to_lowercase();

        match extension.as_str() {
            "tiff" | "tif" => {
                let metadata = tiff_decoder::get_tiff_metadata(file_path)?;
                let result = PyDict::new_bound(py);
                result.set_item("metadata", metadata.to_dict(py)?)?;
                Ok(result.into())
            }
            "czi" => {
                // Placeholder for CZI decoder
                Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                    "CZI format not yet implemented"
                ))
            }
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Unsupported file format: {}", extension)
            )),
        }
    }

    pub fn get_metadata(&self, file_path: &str) -> PyResult<PyObject> {
        let extension = std::path::Path::new(file_path)
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("")
            .to_lowercase();

        match extension.as_str() {
            "tiff" | "tif" => {
                let metadata = tiff_decoder::get_tiff_metadata(file_path)?;
                Python::with_gil(|py| metadata.to_dict(py))
            }
            _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Unsupported file format: {}", extension)
            )),
        }
    }
}

#[pymodule]
fn zstack_decoders(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ZStackDecoder>()?;
    Ok(())
}