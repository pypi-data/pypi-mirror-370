//! # ZeusDB Vector Database - Persistence Module
//!
//! This module handles all save/load operations for ZeusDB vector indexes.
//! It implements a directory-based persistence format with hybrid JSON/Binary storage.
//!
//! ## File Format:
//! ```
//! my_index.zdb/
//! ├── manifest.json           # Index metadata and file list
//! ├── config.json             # Index configuration
//! ├── mappings.bin            # ID mappings (binary)
//! ├── metadata.json           # Vector metadata (JSON)
//! ├── vectors.bin             # Raw vectors (storage mode dependent)
//! ├── quantization.json       # PQ configuration (if enabled)
//! ├── pq_codes.bin            # Quantized codes (if PQ enabled)
//! ├── pq_centroids.bin        # PQ centroids (if trained)
//! └── hnsw_index.hnsw.graph   # HNSW graph (Phase 2)
//! ```

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use chrono::Utc;
use serde_json::Value;
use pyo3::types::{PyDict, PyList};
use std::sync::Arc;
use crate::hnsw_index::{HNSWIndex, StorageMode, QuantizationConfig};
use crate::pq::PQ;


// ============================================================================
// PERSISTENCE DATA STRUCTURES
// ============================================================================

/// Manifest file structure - tracks index metadata and included files
#[derive(Debug, Serialize, Deserialize)]
pub struct IndexManifest {
    pub format_version: String,
    pub zeusdb_version: String,
    pub created_at: String,
    pub saved_at: String,
    pub total_vectors: usize,
    pub index_type: String,
    pub has_quantization: bool,
    pub quantization_trained: bool,
    pub storage_mode: String,
    pub files_included: Vec<String>,
    pub files_excluded: Vec<String>,
    pub total_size_mb: f64,
    pub compression_info: Option<CompressionInfo>,
}

/// Compression statistics for quantized indexes
#[derive(Debug, Serialize, Deserialize)]
pub struct CompressionInfo {
    pub original_size_mb: f64,
    pub compressed_size_mb: f64,
    pub compression_ratio: f64,
}

/// Index configuration for reconstruction
#[derive(Debug, Serialize, Deserialize)]
pub struct IndexConfig {
    pub dim: usize,
    pub space: String,
    pub m: usize,
    pub ef_construction: usize,
    pub expected_size: usize,
    pub id_counter: usize,
    pub vector_count: usize,
}

/// Complete quantization configuration and state
#[derive(Debug, Serialize, Deserialize)]
pub struct QuantizationPersistence {
    pub r#type: String,
    pub subvectors: usize,
    pub bits: usize,
    pub training_size: usize,
    pub max_training_vectors: Option<usize>,
    pub storage_mode: String,
    pub is_trained: bool,
    pub training_completed_at: Option<String>,
    pub memory_stats: Option<MemoryStats>,
    pub pq_config: PQConfig,
    #[serde(default)]
    pub training_ids: Vec<String>,
    #[serde(default)]
    pub training_threshold_reached: bool,
}

/// Memory usage statistics for quantization
#[derive(Debug, Serialize, Deserialize)]
pub struct MemoryStats {
    pub centroid_storage_mb: f64,
    pub compression_ratio: f64,
    pub centroids_per_subvector: usize,
    pub total_centroids: usize,
}

/// Product Quantization configuration details
#[derive(Debug, Serialize, Deserialize)]
pub struct PQConfig {
    pub dim: usize,
    pub sub_dim: usize,
    pub num_centroids: usize,
}

/// ID mappings between external and internal IDs
#[derive(Debug, Serialize, Deserialize, bincode::Encode, bincode::Decode)]
pub struct IdMappings {
    pub id_map: HashMap<String, usize>,
    pub rev_map: HashMap<usize, String>,
}


// ============================================================================
// INDIVIDUAL COMPONENT LOADERS
// ============================================================================

/// Load index configuration from config.json
fn load_config(path: &Path) -> PyResult<IndexConfig> {
    println!("⚙️  Loading config.json...");
    
    let config_path = path.join("config.json");
    let config_data = fs::read_to_string(&config_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read config.json: {}", e)
        )
    })?;
    
    let config: IndexConfig = serde_json::from_str(&config_data).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to parse config.json: {}", e)
        )
    })?;
    
    println!("✅ config.json loaded");
    Ok(config)
}

/// Load ID mappings from mappings.bin
fn load_mappings(path: &Path) -> PyResult<IdMappings> {
    println!("🗂️  Loading mappings.bin...");
    
    let mappings_path = path.join("mappings.bin");
    let mappings_data = fs::read(&mappings_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read mappings.bin: {}", e)
        )
    })?;
    
    let (mappings, _): (IdMappings, usize) = bincode::decode_from_slice(&mappings_data, bincode::config::standard())
        .map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to deserialize mappings.bin: {}", e)
            )
        })?;
    
    println!("✅ mappings.bin loaded");
    Ok(mappings)
}

/// Load vector metadata from metadata.json
fn load_metadata(path: &Path) -> PyResult<HashMap<String, HashMap<String, Value>>> {
    println!("📋 Loading metadata.json...");
    
    let metadata_path = path.join("metadata.json");
    let metadata_data = fs::read_to_string(&metadata_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read metadata.json: {}", e)
        )
    })?;
    
    let metadata: HashMap<String, HashMap<String, Value>> = serde_json::from_str(&metadata_data).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to parse metadata.json: {}", e)
        )
    })?;
    
    println!("✅ metadata.json loaded");
    Ok(metadata)
}

/// Load raw vectors from vectors.bin
fn load_vectors(path: &Path) -> PyResult<HashMap<String, Vec<f32>>> {
    println!("📊 Loading vectors.bin...");
    
    let vectors_path = path.join("vectors.bin");
    
    // Check if vectors.bin exists (might not exist in quantized_only mode)
    if !vectors_path.exists() {
        println!("ℹ️  vectors.bin not found (quantized_only storage mode)");
        return Ok(HashMap::new());
    }
    
    let vectors_data = fs::read(&vectors_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read vectors.bin: {}", e)
        )
    })?;
    
    let (vectors, _): (HashMap<String, Vec<f32>>, usize) = bincode::decode_from_slice(&vectors_data, bincode::config::standard())
        .map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to deserialize vectors.bin: {}", e)
            )
        })?;
    
    println!("✅ vectors.bin loaded");
    Ok(vectors)
}

/// Load manifest for validation and metadata
fn load_manifest(path: &Path) -> PyResult<IndexManifest> {
    println!("📝 Loading manifest.json...");
    
    let manifest_path = path.join("manifest.json");
    let manifest_data = fs::read_to_string(&manifest_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read manifest.json: {}", e)
        )
    })?;
    
    let manifest: IndexManifest = serde_json::from_str(&manifest_data).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to parse manifest.json: {}", e)
        )
    })?;
    
    println!("✅ manifest.json loaded");
    Ok(manifest)
}

/// Load quantization configuration and components (for later implementation)
fn load_quantization(path: &Path) -> PyResult<Option<QuantizationPersistence>> {
    println!("🔧 Loading quantization components...");
    
    let quant_path = path.join("quantization.json");
    if !quant_path.exists() {
        println!("ℹ️  No quantization.json found (non-quantized index)");
        return Ok(None);
    }
    
    let quant_data = fs::read_to_string(&quant_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Failed to read quantization.json: {}", e)
        )
    })?;
    
    let quant_config: QuantizationPersistence = serde_json::from_str(&quant_data).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to parse quantization.json: {}", e)
        )
    })?;
    
    println!("✅ quantization.json loaded");
    
    // TODO: Load PQ centroids and codes if they exist
    // This will be implemented when we handle quantization reconstruction
    
    Ok(Some(quant_config))
}




// ============================================================================
// MAIN PERSISTENCE INTERFACE
// ============================================================================

/// Save an HNSWIndex to a directory structure
pub fn save_index(index: &HNSWIndex, path: &str) -> PyResult<()> {
    println!("🚀 Starting index save to: {}", path);
    
    // Create the directory structure
    let path_buf = Path::new(path);
    fs::create_dir_all(path_buf).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to create directory {}: {}", path, e)
        )
    })?;
    
    // Save components in order of complexity (simple -> complex)
    save_config(index, path_buf)?;
    save_mappings(index, path_buf)?;
    save_metadata(index, path_buf)?;
    
    // Save quantization components if enabled
    if index.has_quantization() {
        save_quantization_config(index, path_buf)?;
        
        if index.can_use_quantization() {
            save_pq_centroids(index, path_buf)?;
            save_pq_codes(index, path_buf)?;
        }
    }
    
    // Save vectors based on storage mode
    save_vectors(index, path_buf)?;
    
    // Save manifest last (references all other files)
    save_manifest(index, path_buf)?;
    
    println!("✅ Index save completed successfully!");
    Ok(())
}



// ============================================================================
// RECONSTRUCTION FUNCTIONS
// ============================================================================

/// Reconstruct HNSWIndex using Simple Reconstruction 
fn reconstruct_index_simple(
    config: IndexConfig,
    mappings: IdMappings,
    metadata: HashMap<String, HashMap<String, Value>>,
    vectors: HashMap<String, Vec<f32>>,
    quantization: Option<QuantizationPersistence>,
) -> PyResult<HNSWIndex> {
    println!("🔧 Creating empty index with loaded configuration...");
    
    // Step 1: Create empty index with loaded config
    let mut index = HNSWIndex::new_empty(
        config.dim,
        config.space.clone(),
        config.m,
        config.ef_construction,
        config.expected_size,
    );
    
    println!("📝 Restoring data fields...");
    
    // Step 2: Restore all data fields directly (but not the graph)
    restore_data_fields(&mut index, mappings, metadata.clone(), vectors.clone(), &config, quantization)?;
    
    println!("🔄 Rebuilding HNSW graph from vectors...");
    
    // Step 3: Rebuild the graph by re-adding all vectors
    rebuild_graph_from_data(&mut index, vectors, metadata)?;
    
    println!("✅ Reconstruction completed!");
    Ok(index)
}




/// Restore all data fields to the index (everything except the HNSW graph)
fn restore_data_fields(
    index: &mut HNSWIndex,
    mappings: IdMappings,
    _metadata: HashMap<String, HashMap<String, Value>>,
    _vectors: HashMap<String, Vec<f32>>,
    config: &IndexConfig,
    quantization: Option<QuantizationPersistence>,
) -> PyResult<()> {
    index.set_id_mappings(mappings.id_map, mappings.rev_map);

    // The add() method will properly:
    // - Insert vectors into index.vectors
    // - Insert metadata into index.vector_metadata  
    // - Update counters correctly
    // - Build the HNSW graph
    
    // Restore counters
    index.set_counters(config.id_counter, config.vector_count);
    
    // Restore quantization state if present
    if let Some(quant_data) = quantization {
        restore_quantization_state_simple(index, quant_data)?;
    }
    
    println!("✅ All data fields restored successfully");
    Ok(())
}



/// Restore quantization state (simplified for reconstruction)
fn restore_quantization_state_simple(
    index: &mut HNSWIndex,
    quant_data: QuantizationPersistence,
) -> PyResult<()> {
    println!("🔧 Restoring quantization state...");

    // Convert QuantizationPersistence back to QuantizationConfig
    let storage_mode = StorageMode::from_string(&quant_data.storage_mode)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

    let quant_config = QuantizationConfig {
        subvectors: quant_data.subvectors,
        bits: quant_data.bits,
        training_size: quant_data.training_size,
        max_training_vectors: quant_data.max_training_vectors,
        storage_mode,
    };

    // Set quantization config
    index.set_quantization_config(Some(quant_config));

    // Restore training IDs
    index.set_training_ids(quant_data.training_ids.clone());

    // Robust threshold logic
    if !quant_data.is_trained {
        // For untrained PQ, recalculate threshold from actual data
        let threshold_should_be_reached = quant_data.training_ids.len() >= quant_data.training_size;
        index.set_training_threshold_reached(threshold_should_be_reached);

        println!(
            "✅ Quantization state restored (untrained, {} training IDs, threshold: {})",
            quant_data.training_ids.len(),
            threshold_should_be_reached
        );
    } else {
        // For trained PQ, use the saved threshold and restore PQ instance
        index.set_training_threshold_reached(quant_data.training_threshold_reached);

        let pq = Arc::new(PQ::new(
            index.get_dim(),
            quant_data.subvectors,
            quant_data.bits,
            quant_data.training_size,
            quant_data.max_training_vectors,
        ));

        pq.set_trained(true);
        index.set_pq(Some(pq));

        println!(
            "✅ Quantization state restored (trained, {} training IDs)",
            quant_data.training_ids.len()
        );
    }

    Ok(())
}





/// Rebuild the HNSW graph by re-inserting all vectors using existing add logic
fn rebuild_graph_from_data(
    index: &mut HNSWIndex,
    vectors: HashMap<String, Vec<f32>>,
    metadata: HashMap<String, HashMap<String, Value>>,
) -> PyResult<()> {
    if vectors.is_empty() {
        println!("ℹ️  No vectors to rebuild (quantized_only mode or empty index)");
        return Ok(());
    }

    println!("🔄 Rebuilding graph with {} vectors...", vectors.len());

    // Prepare batch data for efficient insertion
    let mut batch_vectors = Vec::new();
    let mut batch_ids = Vec::new();
    let mut batch_metadatas = Vec::new();

    // Collect all data maintaining ID consistency
    for (ext_id, vector) in vectors.iter() {
        if let Some(meta) = metadata.get(ext_id) {
            batch_vectors.push(vector.clone());
            batch_ids.push(ext_id.clone());
            batch_metadatas.push(meta.clone());
        }
    }

    println!("📦 Prepared {} vectors for batch insertion", batch_vectors.len());

    // SET FLAG: Prevent training ID collection during rebuild
    index.rebuilding_from_persistence.store(true, std::sync::atomic::Ordering::Release);

    // Use the existing add() method to rebuild the graph
    Python::with_gil(|py| {
        rebuild_using_add_method(index, batch_vectors, batch_ids, batch_metadatas, py)
    })?;

    // 🔥 CLEAR FLAG: Resume normal operation
    index.rebuilding_from_persistence.store(false, std::sync::atomic::Ordering::Release);

    Ok(())

}




/// Helper function to rebuild using the existing add() method
fn rebuild_using_add_method(
    index: &mut HNSWIndex,
    batch_vectors: Vec<Vec<f32>>,
    batch_ids: Vec<String>,
    batch_metadatas: Vec<HashMap<String, Value>>,
    py: Python<'_>,
) -> PyResult<()> {
    use pyo3::types::{PyDict, PyList};
    
    // Convert to Python objects
    let vectors_list = PyList::new(py, &batch_vectors)?;
    let ids_list = PyList::new(py, &batch_ids)?;
    
    // Convert metadata to Python objects
    let metadatas_vec: PyResult<Vec<_>> = batch_metadatas.iter().map(|m| {
        let dict = PyDict::new(py);
        for (k, v) in m {
            dict.set_item(k, convert_json_value_to_python(v, py)?)?;
        }
        Ok(dict)
    }).collect();
    let metadatas_list = PyList::new(py, &metadatas_vec?)?;
    
    // Create batch dictionary
    let batch_dict = PyDict::new(py);
    batch_dict.set_item("vectors", vectors_list)?;
    batch_dict.set_item("ids", ids_list)?;
    batch_dict.set_item("metadatas", metadatas_list)?;
    
    println!("🔄 Calling add() method to rebuild graph...");
    
    // Call the existing add method - this rebuilds the graph automatically
    let result = index.add(batch_dict.into_any(), true)?; // overwrite=true
    
    println!("✅ Graph rebuild completed: {}", result.summary());
    
    // Verify the rebuild
    let final_vector_count = index.get_vector_count();
    println!("📊 Final vector count: {}", final_vector_count);
    
    Ok(())
}

/// Convert JSON Value to Python object (same as before)
fn convert_json_value_to_python(value: &Value, py: Python<'_>) -> PyResult<pyo3::Py<pyo3::PyAny>> {
    
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => {
            let bound = b.into_pyobject(py)?;
            //Ok(bound.unbind().into())
            Ok(bound.to_owned().into())
        },
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.unbind().into())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py)?.unbind().into())
            } else {
                Ok(n.to_string().into_pyobject(py)?.unbind().into())
            }
        },
        Value::String(s) => Ok(s.clone().into_pyobject(py)?.unbind().into()),
        Value::Array(arr) => {
            let py_list = PyList::empty(py);
            for item in arr {
                py_list.append(convert_json_value_to_python(item, py)?)?;
            }
            Ok(py_list.into_pyobject(py)?.unbind().into())
        },
        Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (k, v) in obj {
                py_dict.set_item(k, convert_json_value_to_python(v, py)?)?;
            }
            Ok(py_dict.into_pyobject(py)?.unbind().into())
        }
    }
}





// ============================================================================
// LOAD INTERFACE
// ============================================================================

/// Load an HNSWIndex from a directory structure (Approach B: Simple Reconstruction)
#[pyfunction]
pub fn load_index(path: &str) -> PyResult<HNSWIndex> {
    println!("🚀 Starting index load with reconstruction from: {}", path);
    
    let path_buf = Path::new(path);
    
    // Validate directory exists
    if !path_buf.exists() {
        return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("Index directory not found: {}", path)
        ));
    }
    
    // Phase 1: Load all ZeusDB components
    println!("📋 Phase 1: Loading ZeusDB components...");
    
    let manifest = load_manifest(path_buf)?;
    println!("✅ Manifest loaded: {} vectors, format v{}", 
             manifest.total_vectors, manifest.format_version);
    
    let config = load_config(path_buf)?;
    println!("✅ Config loaded: dim={}, space={}", config.dim, config.space);
    
    let mappings = load_mappings(path_buf)?;
    println!("✅ Mappings loaded: {} ID mappings", mappings.id_map.len());
    
    let metadata = load_metadata(path_buf)?;
    println!("✅ Metadata loaded: {} records", metadata.len());
    
    let vectors = load_vectors(path_buf)?;
    println!("✅ Vectors loaded: {} vectors", vectors.len());
    
    let quantization = load_quantization(path_buf)?;
    if let Some(ref quant) = quantization {
        println!("✅ Quantization loaded: {} subvectors, trained={}", 
                 quant.subvectors, quant.is_trained);
    }

    // Skip HNSW graph loading - we'll rebuild it

    // Phase 2: Create empty index and restore state
    println!("🔧 Phase 2: Creating empty index and restoring state...");
    let restored_index = reconstruct_index_simple(
        config,
        mappings,
        metadata,
        vectors,
        quantization,
    )?;

    println!("✅ Index reconstruction with graph rebuild completed successfully!");
    Ok(restored_index)
}



// ============================================================================
// INDIVIDUAL COMPONENT SAVERS
// ============================================================================

/// Save index configuration as JSON
fn save_config(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    println!("⚙️  Saving config.json...");
    
    let config = IndexConfig {
        dim: index.get_dim(),
        //space: index.get_space().to_string(),
        space: index.space().to_string(),  // Changed from get_space()
        m: index.get_m(),
        ef_construction: index.get_ef_construction(),
        expected_size: index.get_expected_size(),
        id_counter: index.get_id_counter(),
        vector_count: index.get_vector_count(),
    };
    
    let config_path = path.join("config.json");
    let config_json = serde_json::to_string_pretty(&config).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to serialize config: {}", e)
        )
    })?;
    
    fs::write(&config_path, config_json).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to write config.json: {}", e)
        )
    })?;
    
    println!("✅ config.json saved");
    Ok(())
}

/// Save ID mappings using efficient binary format
fn save_mappings(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    println!("🗂️  Saving mappings.bin...");
    
    let id_map = index.get_id_map();
    let rev_map = index.get_rev_map();
    
    let mappings = IdMappings {
        id_map: id_map.clone(),
        rev_map: rev_map.clone(),
    };
    
    let mappings_data = bincode::encode_to_vec(&mappings, bincode::config::standard())
        .map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to serialize mappings: {}", e)
            )
        })?;
    
    let mappings_path = path.join("mappings.bin");
    fs::write(&mappings_path, mappings_data).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to write mappings.bin: {}", e)
        )
    })?;
    
    println!("✅ mappings.bin saved ({} mappings)", id_map.len());
    Ok(())
}

/// Save vector metadata as JSON for external tool compatibility
fn save_metadata(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    println!("📋 Saving metadata.json...");
    
    let vector_metadata = index.get_vector_metadata();
    
    let metadata_path = path.join("metadata.json");
    let metadata_json = serde_json::to_string_pretty(&*vector_metadata).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to serialize metadata: {}", e)
        )
    })?;
    
    fs::write(&metadata_path, metadata_json).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to write metadata.json: {}", e)
        )
    })?;
    
    println!("✅ metadata.json saved ({} records)", vector_metadata.len());
    Ok(())
}

/// Save quantization configuration and training state
fn save_quantization_config(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    if let Some(config) = index.get_quantization_config() {
        println!("🔧 Saving quantization.json...");
        
        let training_completed_at = if index.can_use_quantization() {
            Some(Utc::now().to_rfc3339()) // TODO: Get actual training completion time
        } else {
            None
        };

        // CAPTURE TRAINING STATE:
        let training_ids = index.get_training_ids().clone();
        let training_threshold_reached = index.get_training_threshold_reached();
        
        let (memory_stats, pq_config) = if let Some(pq) = index.get_pq() {
            let (memory_mb, total_centroids) = pq.get_memory_stats();
            
            let memory_stats = MemoryStats {
                centroid_storage_mb: memory_mb,
                compression_ratio: (pq.dim * 4) as f64 / pq.subvectors as f64,
                centroids_per_subvector: pq.num_centroids,
                total_centroids,
            };
            
            let pq_config = PQConfig {
                dim: pq.dim,
                sub_dim: pq.sub_dim,
                num_centroids: pq.num_centroids,
            };
            
            (Some(memory_stats), pq_config)
        } else {
            let pq_config = PQConfig {
                dim: index.get_dim(),
                sub_dim: index.get_dim() / config.subvectors,
                num_centroids: 1 << config.bits,
            };
            (None, pq_config)
        };
        
        let quant_persistence = QuantizationPersistence {
            r#type: "pq".to_string(),
            subvectors: config.subvectors,
            bits: config.bits,
            training_size: config.training_size,
            max_training_vectors: config.max_training_vectors,
            storage_mode: config.storage_mode.to_string().to_string(),
            is_trained: index.can_use_quantization(),
            training_completed_at,
            memory_stats,
            pq_config,
            training_ids,
            training_threshold_reached,
        };
        
        let quant_path = path.join("quantization.json");
        let quant_json = serde_json::to_string_pretty(&quant_persistence).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to serialize quantization config: {}", e)
            )
        })?;
        
        fs::write(&quant_path, quant_json).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to write quantization.json: {}", e)
            )
        })?;
        
        //println!("✅ quantization.json saved");
        println!("✅ quantization.json saved with {} training IDs", quant_persistence.training_ids.len());
    }
    Ok(())
}

/// Save PQ centroids for vector reconstruction
fn save_pq_centroids(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    if let Some(pq) = index.get_pq() {
        if pq.is_trained() {
            println!("🎯 Saving pq_centroids.bin...");
            
            let centroids = pq.centroids.read().unwrap();
            let centroids_data = bincode::encode_to_vec(&*centroids, bincode::config::standard())
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("Failed to serialize PQ centroids: {}", e)
                    )
                })?;
            
            let centroids_path = path.join("pq_centroids.bin");
            fs::write(&centroids_path, centroids_data).map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to write pq_centroids.bin: {}", e)
                )
            })?;
            
            println!("✅ pq_centroids.bin saved");
        }
    }
    Ok(())
}

/// Save quantized vector codes
fn save_pq_codes(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    let pq_codes = index.get_pq_codes();
    if !pq_codes.is_empty() {
        println!("📦 Saving pq_codes.bin...");
        
        let codes_data = bincode::encode_to_vec(&*pq_codes, bincode::config::standard())
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to serialize PQ codes: {}", e)
                )
            })?;
        
        let codes_path = path.join("pq_codes.bin");
        fs::write(&codes_path, codes_data).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to write pq_codes.bin: {}", e)
            )
        })?;
        
        println!("✅ pq_codes.bin saved ({} vectors)", pq_codes.len());
    }
    Ok(())
}

/// Save raw vectors based on storage mode configuration
fn save_vectors(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    let vectors = index.get_vectors();
    if !vectors.is_empty() {
        println!("📊 Saving vectors.bin...");
        
        let vectors_data = bincode::encode_to_vec(&*vectors, bincode::config::standard())
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("Failed to serialize vectors: {}", e)
                )
            })?;
        
        let vectors_path = path.join("vectors.bin");
        fs::write(&vectors_path, vectors_data).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to write vectors.bin: {}", e)
            )
        })?;
        
        println!("✅ vectors.bin saved ({} vectors)", vectors.len());
    }
    Ok(())
}


/// Save manifest file (must be last - references all other files)
fn save_manifest(index: &HNSWIndex, path: &Path) -> PyResult<()> {
    println!("📝 Saving manifest.json...");
    
    let vectors = index.get_vectors();
    let pq_codes = index.get_pq_codes();
    let vector_count = index.get_vector_count();
    
    // Determine what files are included based on what we actually saved
    let mut files_included = vec![
        "config.json".to_string(),
        "mappings.bin".to_string(),
        "metadata.json".to_string(),
    ];
    
    let mut files_excluded = Vec::new();
    
    // Add quantization files if they exist
    if index.has_quantization() {
        files_included.push("quantization.json".to_string());
        
        if index.can_use_quantization() {
            files_included.push("pq_centroids.bin".to_string());
            if !pq_codes.is_empty() {
                files_included.push("pq_codes.bin".to_string());
            }
        }
    }
    
    // Add vectors.bin if it was saved
    if !vectors.is_empty() {
        files_included.push("vectors.bin".to_string());
    } else {
        files_excluded.push("vectors.bin".to_string());
    }

    // Phase 2: Add HNSW graph files
    // REPLACE WITH THIS CONDITIONAL LOGIC:
    let vector_count = index.get_vector_count();
    if vector_count > 0 {
        files_included.push("hnsw_index.hnsw.graph".to_string());
        files_excluded.push("hnsw_index.hnsw.data".to_string());
        println!("📋 Graph files in manifest:");
        println!("   ✅ Included: hnsw_index.hnsw.graph");
        println!("   ❌ Excluded: hnsw_index.hnsw.data (we use our own data files)");
    } else {
        files_excluded.push("hnsw_index.hnsw.graph".to_string());
        files_excluded.push("hnsw_index.hnsw.data".to_string());
        println!("ℹ️  No graph files (empty index)");
    }

    
    // Calculate compression info for quantized indexes
    let compression_info = if index.has_quantization() && index.can_use_quantization() && !pq_codes.is_empty() {
        let raw_size_mb = (vectors.len() * index.get_dim() * 4) as f64 / (1024.0 * 1024.0);
        let compressed_size_mb = (pq_codes.len() * index.get_quantization_subvectors()) as f64 / (1024.0 * 1024.0);
        let compression_ratio = if compressed_size_mb > 0.0 {
            raw_size_mb / compressed_size_mb
        } else {
            1.0
        };
        
        Some(CompressionInfo {
            original_size_mb: raw_size_mb,
            compressed_size_mb,
            compression_ratio,
        })
    } else {
        None
    };
    
    // Calculate total directory size
    let total_size_mb = calculate_directory_size(path).unwrap_or(0.0);
    
    let manifest = IndexManifest {
        format_version: "1.0.0".to_string(),
        zeusdb_version: env!("CARGO_PKG_VERSION").to_string(),
        created_at: index.get_created_at().to_string(),
        saved_at: Utc::now().to_rfc3339(),
        total_vectors: vector_count,
        index_type: "HNSW".to_string(),
        has_quantization: index.has_quantization(),
        quantization_trained: index.can_use_quantization(),
        storage_mode: index.get_storage_mode(),
        files_included,
        files_excluded,
        total_size_mb,
        compression_info,
    };
    
    let manifest_path = path.join("manifest.json");
    let manifest_json = serde_json::to_string_pretty(&manifest).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to serialize manifest: {}", e)
        )
    })?;
    
    fs::write(&manifest_path, manifest_json).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            format!("Failed to write manifest.json: {}", e)
        )
    })?;
    
    println!("✅ manifest.json saved");
    Ok(())
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/// Calculate the total size of a directory in MB
fn calculate_directory_size(path: &Path) -> Result<f64, std::io::Error> {
    let mut total_size = 0u64;
    
    if path.is_dir() {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let metadata = entry.metadata()?;
            
            if metadata.is_file() {
                total_size += metadata.len();
            }
        }
    }
    
    Ok(total_size as f64 / (1024.0 * 1024.0))
}

// ============================================================================
// VALIDATION HELPERS (for Phase 3)
// ============================================================================

/// Check if a path contains a valid ZeusDB index (Phase 3)
pub fn is_valid_index(_path: &str) -> bool {
    // TODO: Implement in Phase 3
    false
}

/// Get index information without full loading (Phase 3)
pub fn get_index_info(_path: &str) -> Option<IndexManifest> {
    // TODO: Implement in Phase 3
    None
}
