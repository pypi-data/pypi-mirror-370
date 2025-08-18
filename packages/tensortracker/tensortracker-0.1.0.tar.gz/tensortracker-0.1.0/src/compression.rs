use std::io;
use zstd::bulk::{Compressor, Decompressor};

/// Compresses data using zstd compression
pub fn compress_data(data: &[u8], level: i32) -> io::Result<Vec<u8>> {
    let mut compressor = Compressor::new(level)?;
    compressor.compress(data).map_err(|e| io::Error::other(e))
}

/// Decompresses zstd compressed data
pub fn decompress_data(compressed: &[u8], original_size: usize) -> io::Result<Vec<u8>> {
    let mut decompressor = Decompressor::new()?;
    decompressor.decompress(compressed, original_size).map_err(|e| io::Error::other(e))
}

/// Calculates the optimal compression level based on tensor size and type
pub fn optimal_compression_level(size: usize, is_fp16: bool) -> i32 {
    if size < 1024 * 1024 { // < 1MB
        return 1; // Light compression for small tensors
    }
    if is_fp16 {
        3 // Moderate compression for fp16 tensors
    } else {
        5 // Higher compression for other types
    }
}
