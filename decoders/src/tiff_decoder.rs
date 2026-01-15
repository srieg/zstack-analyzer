use crate::metadata::ImageMetadata;
use anyhow::{Context, Result};
use pyo3::prelude::*;
use std::fs::File;
use std::io::BufReader;
use tiff::decoder::{Decoder, DecodingResult};
use tiff::ColorType;

pub fn _decode_tiff(file_path: &str) -> PyResult<(Vec<Vec<Vec<u16>>>, ImageMetadata)> {
    let file = File::open(file_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file: {}", e)))?;
    
    let mut decoder = Decoder::new(BufReader::new(file))
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create TIFF decoder: {}", e)))?;
    
    let (width, height) = decoder.dimensions()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get dimensions: {}", e)))?;
    
    let color_type = decoder.colortype()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get color type: {}", e)))?;
    
    let mut metadata = ImageMetadata::new();
    metadata.width = width;
    metadata.height = height;
    metadata.depth = 1; // Will be updated if we find multiple pages
    
    match color_type {
        ColorType::Gray(8) => metadata.bit_depth = 8,
        ColorType::Gray(16) => metadata.bit_depth = 16,
        ColorType::RGB(8) => {
            metadata.bit_depth = 8;
            metadata.channels = 3;
        }
        ColorType::RGB(16) => {
            metadata.bit_depth = 16;
            metadata.channels = 3;
        }
        _ => {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Unsupported color type: {:?}", color_type)
            ));
        }
    }
    
    // For now, decode first page only
    // TODO: Implement multi-page TIFF support for Z-stacks
    let image_data = decoder.read_image()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to read image: {}", e)))?;
    
    let data_3d = match image_data {
        DecodingResult::U8(data) => {
            // Convert u8 to u16 for consistency
            let converted: Vec<u16> = data.iter().map(|&x| x as u16).collect();
            vec![vec![converted]]
        }
        DecodingResult::U16(data) => {
            vec![vec![data]]
        }
        _ => {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Unsupported data type"
            ));
        }
    };
    
    Ok((data_3d, metadata))
}

pub fn get_tiff_metadata(file_path: &str) -> PyResult<ImageMetadata> {
    let file = File::open(file_path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file: {}", e)))?;
    
    let mut decoder = Decoder::new(BufReader::new(file))
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create TIFF decoder: {}", e)))?;
    
    let (width, height) = decoder.dimensions()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get dimensions: {}", e)))?;
    
    let color_type = decoder.colortype()
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to get color type: {}", e)))?;
    
    let mut metadata = ImageMetadata::new();
    metadata.width = width;
    metadata.height = height;
    metadata.depth = 1;
    
    match color_type {
        ColorType::Gray(8) => metadata.bit_depth = 8,
        ColorType::Gray(16) => metadata.bit_depth = 16,
        ColorType::RGB(8) => {
            metadata.bit_depth = 8;
            metadata.channels = 3;
        }
        ColorType::RGB(16) => {
            metadata.bit_depth = 16;
            metadata.channels = 3;
        }
        _ => {
            metadata.bit_depth = 0; // Unknown
        }
    }
    
    Ok(metadata)
}