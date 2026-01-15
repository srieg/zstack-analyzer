use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImageMetadata {
    pub width: u32,
    pub height: u32,
    pub depth: u32,
    pub channels: u32,
    pub bit_depth: u16,
    pub pixel_size_x: Option<f64>,
    pub pixel_size_y: Option<f64>,
    pub pixel_size_z: Option<f64>,
    pub acquisition_date: Option<String>,
    pub microscope_info: Option<String>,
    pub objective_info: Option<String>,
    pub channel_names: Vec<String>,
    pub exposure_times: Vec<f64>,
    pub custom_metadata: HashMap<String, String>,
}

impl ImageMetadata {
    pub fn new() -> Self {
        ImageMetadata {
            width: 0,
            height: 0,
            depth: 0,
            channels: 0,
            bit_depth: 0,
            pixel_size_x: None,
            pixel_size_y: None,
            pixel_size_z: None,
            acquisition_date: None,
            microscope_info: None,
            objective_info: None,
            channel_names: Vec::new(),
            exposure_times: Vec::new(),
            custom_metadata: HashMap::new(),
        }
    }

    pub fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        
        dict.set_item("width", self.width)?;
        dict.set_item("height", self.height)?;
        dict.set_item("depth", self.depth)?;
        dict.set_item("channels", self.channels)?;
        dict.set_item("bit_depth", self.bit_depth)?;
        
        if let Some(px) = self.pixel_size_x {
            dict.set_item("pixel_size_x", px)?;
        }
        if let Some(py_size) = self.pixel_size_y {
            dict.set_item("pixel_size_y", py_size)?;
        }
        if let Some(pz) = self.pixel_size_z {
            dict.set_item("pixel_size_z", pz)?;
        }
        
        if let Some(ref date) = self.acquisition_date {
            dict.set_item("acquisition_date", date)?;
        }
        if let Some(ref microscope) = self.microscope_info {
            dict.set_item("microscope_info", microscope)?;
        }
        if let Some(ref objective) = self.objective_info {
            dict.set_item("objective_info", objective)?;
        }
        
        dict.set_item("channel_names", &self.channel_names)?;
        dict.set_item("exposure_times", &self.exposure_times)?;
        
        let custom_dict = PyDict::new_bound(py);
        for (key, value) in &self.custom_metadata {
            custom_dict.set_item(key, value)?;
        }
        dict.set_item("custom_metadata", custom_dict)?;
        
        Ok(dict.into())
    }
}