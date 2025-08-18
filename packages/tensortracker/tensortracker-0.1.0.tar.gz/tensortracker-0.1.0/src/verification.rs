use std::io;
use sha2::{Sha256, Digest};
use safetensors::SafeTensors;

/// Verifies the integrity of a tensor patch using SHA-256
pub fn verify_patch(patch_data: &[u8], expected_hash: &str) -> bool {
    let mut hasher = Sha256::new();
    hasher.update(patch_data);
    let hash = format!("{:x}", hasher.finalize());
    hash == expected_hash
}

/// Calculates a deterministic hash for a SafeTensor
pub fn hash_safetensor(tensor: &SafeTensors) -> io::Result<String> {
    let mut hasher = Sha256::new();
    let mut tensor_names: Vec<&String> = tensor.names();
    tensor_names.sort(); // Ensure deterministic ordering
    
    for name in tensor_names {
        if let Ok(view) = tensor.tensor(name) {
            hasher.update(name.as_bytes());
            hasher.update(view.data());
        }
    }
    
    Ok(format!("{:x}", hasher.finalize()))
}

/// Validates patch application by comparing resulting hash
pub fn validate_patch_result(result: &SafeTensors, expected_hash: &str) -> bool {
    match hash_safetensor(result) {
        Ok(hash) => hash == expected_hash,
        Err(_) => false
    }
}
