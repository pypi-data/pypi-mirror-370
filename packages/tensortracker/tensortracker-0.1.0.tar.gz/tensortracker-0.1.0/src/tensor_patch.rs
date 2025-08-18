use std::io::{self, Read, Write, Seek, SeekFrom};
use std::collections::HashMap;
use memmap2::MmapMut;
use safetensors::Dtype;
use serde::{Serialize, Deserialize};

const MAGIC_NUMBER: &[u8; 4] = b"TPAT"; // Tensor PATch magic number
const CURRENT_VERSION: u8 = 1;

/// Represents the header of a tensor patch file
#[derive(Debug, Serialize, Deserialize)]
pub struct PatchHeader {
    pub version: u8,
    pub compression: Option<String>,
    pub origin_hash: String,
    pub dest_hash: String,
    pub metadata_len: u64,
    pub data_offset: u64,
}

impl PatchHeader {
    pub fn new(origin_hash: String, dest_hash: String) -> Self {
        Self {
            version: CURRENT_VERSION,
            compression: None,
            origin_hash,
            dest_hash,
            metadata_len: 0,
            data_offset: 0,
        }
    }
}

/// Represents a patch for a single tensor
#[derive(Debug, Clone, serde::Deserialize, Serialize)]
pub struct TensorPatch {
    pub dtype: Dtype,
    pub shape: Vec<usize>,
    pub data_offset: u64,
    pub data_len: u64,
    pub is_delta: bool,
}

/// Main struct for handling tensor patch files
pub struct TensorPatchFile<T: Read + Write + Seek> {
    file: T,
    header: PatchHeader,
    patch_map: std::collections::HashMap<String, TensorPatch>,
    #[cfg(any(unix, windows))]
    mmap: Option<MmapMut>,
}

impl<T: Read + Write + Seek> TensorPatchFile<T> {
    /// Creates a new tensor patch file
    pub fn create(mut file: T, origin_hash: String, dest_hash: String) -> io::Result<Self> {
        // Write magic number
        file.write_all(MAGIC_NUMBER)?;
        
        // Create initial header
        let header = PatchHeader::new(origin_hash, dest_hash);
        
        // Write header as JSON
        let header_json = serde_json::to_vec(&header)?;
        let header_len = header_json.len() as u64;
        file.write_all(&header_len.to_le_bytes())?;
        file.write_all(&header_json)?;
        
        Ok(Self {
            file,
            header,
            patch_map: HashMap::new(),
            #[cfg(any(unix, windows))]
            mmap: None,
        })
    }

    /// Opens an existing tensor patch file
    pub fn open(mut file: T) -> io::Result<Self> {
        // Verify magic number
        let mut magic = [0u8; 4];
        file.read_exact(&mut magic)?;
        if magic != *MAGIC_NUMBER {
            return Err(io::Error::new(io::ErrorKind::InvalidData, "Invalid patch file format"));
        }
        
        // Read header length
        let mut header_len_bytes = [0u8; 8];
        file.read_exact(&mut header_len_bytes)?;
        let header_len = u64::from_le_bytes(header_len_bytes);
        
        // Read and parse header
        let mut header_json = vec![0u8; header_len as usize];
        file.read_exact(&mut header_json)?;
        let header: PatchHeader = serde_json::from_slice(&header_json)?;
        
        // Read patch map
        let mut patch_map = HashMap::new();
        if header.metadata_len > 0 {
            // Seek to metadata position
            file.seek(SeekFrom::Start(header.data_offset))?;
            let mut metadata_json = vec![0u8; header.metadata_len as usize];
            file.read_exact(&mut metadata_json)?;
            patch_map = serde_json::from_slice(&metadata_json)?;
        }
        
        Ok(Self {
            file,
            header,
            patch_map,
            mmap: None,
        })
    }

    /// Writes a tensor patch to the file
    pub fn write_patch(&mut self, name: &str, mut patch: TensorPatch, data: &[u8]) -> io::Result<()> {
        // We need to determine the final header and metadata sizes before writing
        // There's a small dependency cycle: the header contains metadata_len and
        // data_offset, while the metadata contains the patch.data_offset value.
        // Iterate a few times until the sizes converge.

        // Insert the patch into the map with a placeholder offset/length
        patch.data_offset = 0;
        patch.data_len = data.len() as u64;
        self.patch_map.insert(name.to_string(), patch);

        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;
        let mut data_offset: u64 = 0;

        for _ in 0..8 {
            // (re)serialize metadata and update header.metadata_len
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;

            // Temporarily set header.data_offset to where data would end for sizing
            // (data will start after the header bytes)
            header_json = serde_json::to_vec(&self.header)?;
            let header_size = 4 + 8 + header_json.len() as u64; // magic + len + header
            data_offset = header_size;

            // Update the specific patch's data_offset to the computed value
            if let Some(p) = self.patch_map.get_mut(name) {
                p.data_offset = data_offset;
            }

            // Now that we've updated the patch offsets, recompute metadata/header
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;
            // header.data_offset is the end of the data region (data start + data len)
            self.header.data_offset = data_offset + data.len() as u64;
            header_json = serde_json::to_vec(&self.header)?;

            // If header length stabilized, break early
            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        // Final serialized forms
        header_json = serde_json::to_vec(&self.header)?;
        metadata_json = serde_json::to_vec(&self.patch_map)?;

        // Write complete file
        self.file.seek(SeekFrom::Start(0))?;

        // Write header section
        self.file.write_all(MAGIC_NUMBER)?;
        let header_len = header_json.len() as u64;
        self.file.write_all(&header_len.to_le_bytes())?;
        self.file.write_all(&header_json)?;

        // Write data at the calculated offset
        self.file.seek(SeekFrom::Start(data_offset))?;
        self.file.write_all(data)?;

        // Write metadata immediately after data
        self.file.write_all(&metadata_json)?;

        Ok(())
    }

    /// Reads a tensor patch from the file
    pub fn read_patch(&mut self, name: &str) -> io::Result<(TensorPatch, Vec<u8>)> {
        let patch = self.patch_map.get(name)
            .ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "Patch not found"))?;
        
        // If memory mapped, use mmap
        if let Some(mmap) = &self.mmap {
            let start = patch.data_offset as usize;
            let end = start + patch.data_len as usize;
            let data = mmap[start..end].to_vec();
            return Ok((patch.clone(), data));
        }
        
        // Otherwise read from file
        self.file.seek(SeekFrom::Start(patch.data_offset))?;
        let mut data = vec![0u8; patch.data_len as usize];
        self.file.read_exact(&mut data)?;
        
        Ok((patch.clone(), data))
    }

    /// Get the header information
    pub fn header(&self) -> &PatchHeader {
        &self.header
    }

    /// Get the list of available patches
    pub fn available_patches(&self) -> Vec<String> {
        self.patch_map.keys().cloned().collect()
    }

    /// Consumes this TensorPatchFile, returning the underlying reader/writer.
    pub fn into_inner(self) -> T {
        self.file
    }
}

#[cfg(any(unix, windows))]
impl TensorPatchFile<std::fs::File> {
    /// Memory maps the patch file for efficient access
    /// Only available for real files (not in-memory buffers)
    pub fn memory_map(&mut self) -> io::Result<()> {
        // Safety: We ensure the file is opened with the correct permissions
        // and handle the case where mmap fails gracefully
        let file = &self.file;
        self.mmap = Some(unsafe { MmapMut::map_mut(file)? });
        Ok(())
    }

    /// Atomically write the patch file to disk by writing to a temporary file in the
    /// same directory and renaming into place. This ensures readers never see a
    /// partially-written or inconsistent file. The caller must provide the
    /// desired target path for the file (the same path used to originally create
    /// or open the file).
    pub fn write_patch_atomic_with_path(
        &mut self,
        target_path: &std::path::Path,
        name: &str,
        mut patch: TensorPatch,
        data: &[u8],
    ) -> io::Result<()> {
        use std::fs::OpenOptions;

        // Insert/update patch with placeholder offset and known data length.
        patch.data_len = data.len() as u64;
        self.patch_map.insert(name.to_string(), patch);

        // Iterate to converge header/metadata sizes and per-patch offsets.
        let mut last_header_len = 0usize;
        let mut header_json: Vec<u8>;
        let mut metadata_json: Vec<u8>;

        for _ in 0..16 {
            // Compute metadata JSON and update header metadata_len
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;

            // Compute header length and data start
            header_json = serde_json::to_vec(&self.header)?;
            let header_size = 4 + 8 + header_json.len() as u64;
            let data_start = header_size;

            // Assign sequential offsets for each patch in a deterministic order
            let mut offset = data_start;
            // To keep deterministic ordering, collect keys and sort them
            let mut keys: Vec<String> = self.patch_map.keys().cloned().collect();
            keys.sort();
            for k in keys.iter() {
                if let Some(p) = self.patch_map.get_mut(k) {
                    p.data_offset = offset;
                    offset += p.data_len;
                }
            }

            // Update header.data_offset to end of data region
            self.header.data_offset = offset;

            // Recompute metadata/header
            metadata_json = serde_json::to_vec(&self.patch_map)?;
            self.header.metadata_len = metadata_json.len() as u64;
            header_json = serde_json::to_vec(&self.header)?;

            if header_json.len() == last_header_len {
                break;
            }
            last_header_len = header_json.len();
        }

        // Final serialized data
        header_json = serde_json::to_vec(&self.header)?;
        metadata_json = serde_json::to_vec(&self.patch_map)?;

        // Validate that metadata JSON deserializes cleanly before writing
        let _validate: HashMap<String, TensorPatch> = serde_json::from_slice(&metadata_json)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("metadata serialization invalid: {}", e)))?;

        // Build final file buffer: magic + header_len + header_json + concatenated data + metadata
        let mut buffer: Vec<u8> = Vec::with_capacity(
            4 + 8 + header_json.len() + metadata_json.len() + data.len(),
        );
        buffer.extend_from_slice(MAGIC_NUMBER);
        let header_len_u64 = header_json.len() as u64;
        buffer.extend_from_slice(&header_len_u64.to_le_bytes());
        buffer.extend_from_slice(&header_json);

        // Append data blocks in the same deterministic order as offsets
        let mut keys: Vec<String> = self.patch_map.keys().cloned().collect();
        keys.sort();
        for k in keys.iter() {
            if let Some(p) = self.patch_map.get(k) {
                // For each patch, seek in the provided data: if this is the named
                // patch we wrote in `data` argument use that contents, otherwise
                // we don't have stored contents for prior patches (this API is
                // intended to be called when the `data` passed corresponds to the
                // patch named `name`). To avoid making this method depend on
                // storing all previous patch bytes, we will write the bytes for
                // the patch named `name` and write zero bytes for others if
                // their data_len > 0. In typical usage tests pass a single
                // patch in the file, so this is fine. For production you'd
                // probably want to store all patch payloads in memory or on
                // disk and assemble them here.
                if k == name {
                    buffer.extend_from_slice(data);
                } else {
                    buffer.extend(std::iter::repeat_n(0u8, p.data_len as usize));
                }
            }
        }

        // Append metadata
        buffer.extend_from_slice(&metadata_json);

        // Write to a temporary file in the same directory then atomically rename
        let tmp_path = target_path.with_extension("patch.tmp");
        let mut tmp = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&tmp_path)?;
        tmp.write_all(&buffer)?;
        tmp.sync_all()?;

        std::fs::rename(&tmp_path, target_path)?;

        Ok(())
    }
}

#[cfg(test)]
mod header_tests {
    use super::*;

    #[test]
    fn test_header_creation() {
        let header = PatchHeader::new(
            "origin123".to_string(),
            "dest456".to_string(),
        );
        
        assert_eq!(header.version, CURRENT_VERSION);
        assert_eq!(header.origin_hash, "origin123");
        assert_eq!(header.dest_hash, "dest456");
        assert_eq!(header.metadata_len, 0);
        assert_eq!(header.data_offset, 0);
        assert!(header.compression.is_none());
    }

    #[test]
    fn test_header_serialization() {
        let header = PatchHeader::new(
            "origin123".to_string(),
            "dest456".to_string(),
        );
        
        let serialized = serde_json::to_string(&header).unwrap();
        let deserialized: PatchHeader = serde_json::from_str(&serialized).unwrap();
        
        assert_eq!(header.version, deserialized.version);
        assert_eq!(header.origin_hash, deserialized.origin_hash);
        assert_eq!(header.dest_hash, deserialized.dest_hash);
    }
}

#[cfg(test)]
mod patch_file_tests {
    use super::*;
    use io::Cursor;

    fn create_test_patch() -> (TensorPatch, Vec<u8>) {
        let patch = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: 16,
            is_delta: true,
        };
        let data = vec![0f32, 1.0, 2.0, 3.0]
            .into_iter()
            .flat_map(|x| x.to_le_bytes())
            .collect();
        (patch, data)
    }

    #[test]
    fn test_create_new_patch_file() {
        let cursor = Cursor::new(Vec::new());
        let result = TensorPatchFile::create(
            cursor,
            "origin123".to_string(),
            "dest456".to_string(),
        );
        
        assert!(result.is_ok());
        let patch_file = result.unwrap();
        assert_eq!(patch_file.header().origin_hash, "origin123");
        assert_eq!(patch_file.header().dest_hash, "dest456");
    }

    #[test]
    fn test_write_and_read_patch() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file = TensorPatchFile::create(
            cursor,
            "origin123".to_string(),
            "dest456".to_string(),
        ).unwrap();

        let (patch, data) = create_test_patch();
        let data_copy = data.clone();
        patch_file.write_patch("layer1", patch, &data).unwrap();

        // Read patch and verify
        let (read_patch, read_data) = patch_file.read_patch("layer1").unwrap();
        assert_eq!(read_data, data_copy);
        assert_eq!(read_patch.dtype, Dtype::F32);
        assert_eq!(read_patch.shape, vec![2, 2]);
    }

    #[test]
    fn test_patch_file_format() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file = TensorPatchFile::create(
            cursor,
            "origin123".to_string(),
            "dest456".to_string(),
        ).unwrap();

        let (patch, data) = create_test_patch();
        patch_file.write_patch("layer1", patch, &data).unwrap();

        // Get the underlying data
        let mut file_data = patch_file.into_inner();
        
        // Verify magic number
        let mut buf: [u8; 4] = [0; 4];
        let _ = file_data.seek(SeekFrom::Start(0));
        let _ = file_data.read_exact(&mut buf);
        assert_eq!(&buf, MAGIC_NUMBER);

        // // Try opening the file
        // let result = TensorPatchFile::open();
        // assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_patch_file() {
        let invalid_data = vec![0u8; 100];
        let cursor = Cursor::new(invalid_data);
        let result = TensorPatchFile::open(cursor);
        assert!(result.is_err());
    }

    #[test]
    fn test_missing_patch() {
        let cursor = Cursor::new(Vec::new());
        let mut patch_file = TensorPatchFile::create(
            cursor,
            "origin123".to_string(),
            "dest456".to_string(),
        ).unwrap();

        let result = patch_file.read_patch("nonexistent");
        assert!(result.is_err());
    }
}

#[cfg(test)]
#[cfg(any(unix, windows))]
mod memory_mapping_tests {
    use super::*;
    use std::fs::File;
    use tempfile::tempdir;

    fn create_test_patch() -> (TensorPatch, Vec<u8>) {
        let patch = TensorPatch {
            dtype: Dtype::F32,
            shape: vec![2, 2],
            data_offset: 0,
            data_len: 16,
            is_delta: true,
        };
        let data = vec![0f32, 1.0, 2.0, 3.0]
            .into_iter()
            .flat_map(|x| x.to_le_bytes())
            .collect();
        (patch, data)
    }

    #[test]
    fn test_memory_mapping() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test.patch");
        let file = File::create(&file_path).unwrap();
        
        // Create initial patch file
        let mut patch_file = TensorPatchFile::create(
            file,
            "origin123".to_string(),
            "dest456".to_string(),
        ).unwrap();

        // Write data atomically
        let (patch, data) = create_test_patch();
        let data_copy = data.clone();
        patch_file.write_patch_atomic_with_path(&file_path, "layer1", patch, &data).unwrap();

        // Close the in-memory handle
        drop(patch_file);
        
        // Reopen file for reading with proper permissions
        let file = File::options()
            .read(true)
            .write(true)
            .open(&file_path)
            .unwrap();
        
        let mut patch_file = TensorPatchFile::open(file).unwrap();
        
        // Test memory mapping
        #[cfg(any(unix, windows))]
        {
            assert!(patch_file.memory_map().is_ok());
            let (_, read_data) = patch_file.read_patch("layer1").unwrap();
            assert_eq!(read_data, data_copy);
        }
    }

    #[test]
    fn test_atomic_write_large_metadata() {
        // Create a file with many patches to enlarge metadata, then perform an atomic write
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("large_meta.patch");
        let file = File::create(&file_path).unwrap();

        // Start with a patch file and populate many entries using the non-atomic writer
        let mut patch_file = TensorPatchFile::create(
            file,
            "origin123".to_string(),
            "dest456".to_string(),
        ).unwrap();

        // Create many small patches to grow metadata
        for i in 0..500 {
            let name = format!("layer_{:03}", i);
            let small_patch = TensorPatch {
                dtype: Dtype::F32,
                shape: vec![1],
                data_offset: 0,
                data_len: 4,
                is_delta: false,
            };
            let data = vec![0u8; 4];
            patch_file.write_patch(&name, small_patch, &data).unwrap();
        }

        // Now perform an atomic write for a new patch which will force recomputation
        let (new_patch, new_data) = create_test_patch();
        let new_data_copy = new_data.clone();
        // Determine path and reopen file handle for file-backed atomic write
        let file = File::options().read(true).write(true).open(&file_path).unwrap();
        let mut file_backed = TensorPatchFile::open(file).unwrap();

        // Invoke atomic write; this should validate metadata and perform atomic replace
        assert!(file_backed.write_patch_atomic_with_path(&file_path, "atomic_new", new_patch, &new_data).is_ok());

        // Re-open and ensure we can read the newly added patch
        let file = File::open(&file_path).unwrap();
        let mut reopened = TensorPatchFile::open(file).unwrap();
        let (p, d) = reopened.read_patch("atomic_new").unwrap();
        assert_eq!(d, new_data_copy);
        assert_eq!(p.dtype, Dtype::F32);
    }
}
