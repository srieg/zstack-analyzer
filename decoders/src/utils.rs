use std::path::Path;

pub fn get_file_extension(file_path: &str) -> Option<String> {
    Path::new(file_path)
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.to_lowercase())
}

pub fn is_supported_format(file_path: &str) -> bool {
    match get_file_extension(file_path) {
        Some(ext) => matches!(ext.as_str(), "tiff" | "tif" | "czi" | "nd2" | "lsm"),
        None => false,
    }
}

pub fn estimate_memory_usage(width: u32, height: u32, depth: u32, channels: u32, bit_depth: u16) -> u64 {
    let bytes_per_pixel = match bit_depth {
        8 => 1,
        16 => 2,
        32 => 4,
        _ => 2, // Default to 16-bit
    };
    
    (width as u64) * (height as u64) * (depth as u64) * (channels as u64) * (bytes_per_pixel as u64)
}