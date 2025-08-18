#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::types::PyDict;
#[cfg(feature = "python")]
use std::collections::HashMap;
#[cfg(feature = "python")]
use std::path::Path;

#[cfg(feature = "python")]
use crate::XacroProcessor;

#[cfg(feature = "python")]
#[pyclass]
pub struct PyXacroProcessor {
    processor: XacroProcessor,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyXacroProcessor {
    #[new]
    fn new(verbosity: Option<u8>) -> Self {
        Self {
            processor: XacroProcessor::new(verbosity.unwrap_or(1)),
        }
    }

    fn set_format_output(&mut self, format: bool) {
        self.processor.set_format_output(format);
    }

    fn set_remove_root_link(&mut self, link_name: Option<String>) {
        self.processor.set_remove_root_link(link_name);
    }

    fn set_validate_urdf(&mut self, validate: bool) {
        self.processor.set_validate_urdf(validate);
    }

    fn set_validation_verbose(&mut self, verbose: bool) {
        self.processor.set_validation_verbose(verbose);
    }

    fn process_file(&mut self, input_file: &str, mappings: Option<&PyDict>) -> PyResult<String> {
        let mappings = if let Some(dict) = mappings {
            let mut map = HashMap::new();
            for (key, value) in dict {
                let key: String = key.extract()?;
                let value: String = value.extract()?;
                map.insert(key, value);
            }
            Some(map)
        } else {
            None
        };

        // Convert to absolute path if not already absolute
        let input_path = if Path::new(input_file).is_absolute() {
            Path::new(input_file).to_path_buf()
        } else {
            std::env::current_dir()
                .map_err(|e| {
                    pyo3::exceptions::PyIOError::new_err(format!(
                        "Cannot get current directory: {}",
                        e
                    ))
                })?
                .join(input_file)
        };

        match self.processor.process_file(&input_path, mappings) {
            Ok(doc) => Ok(self
                .processor
                .element_to_string_with_source(&doc, Some(&input_path.display().to_string()))),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
        }
    }

    fn process_string(&mut self, xml_content: &str, mappings: Option<&PyDict>) -> PyResult<String> {
        let mappings = if let Some(dict) = mappings {
            let mut map = HashMap::new();
            for (key, value) in dict {
                let key: String = key.extract()?;
                let value: String = value.extract()?;
                map.insert(key, value);
            }
            Some(map)
        } else {
            None
        };

        match self.processor.process_string(xml_content, mappings) {
            Ok(doc) => Ok(self.processor.element_to_string(&doc)),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
        }
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_to_string(
    input_file: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_root_link: Option<&str>,
    validate_urdf: Option<bool>,
    validation_verbose: Option<bool>,
) -> PyResult<String> {
    let mut processor = XacroProcessor::new(verbosity.unwrap_or(1));
    processor.set_format_output(format_output.unwrap_or(true)); // Format output by default
    processor.set_remove_root_link(remove_root_link.map(|s| s.to_string()));
    processor.set_validate_urdf(validate_urdf.unwrap_or(true)); // Validation enabled by default
    processor.set_validation_verbose(validation_verbose.unwrap_or(true));

    let mappings = if let Some(dict) = mappings {
        let mut map = HashMap::new();
        for (key, value) in dict {
            let key: String = key.extract()?;
            let value: String = value.extract()?;
            map.insert(key, value);
        }
        Some(map)
    } else {
        None
    };

    // Convert to absolute path if not already absolute
    let input_path = if Path::new(input_file).is_absolute() {
        Path::new(input_file).to_path_buf()
    } else {
        std::env::current_dir()
            .map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Cannot get current directory: {}", e))
            })?
            .join(input_file)
    };

    match processor.process_file(&input_path, mappings) {
        Ok(doc) => {
            Ok(processor
                .element_to_string_with_source(&doc, Some(&input_path.display().to_string())))
        }
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_from_string(
    xml_content: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_root_link: Option<&str>,
    validate_urdf: Option<bool>,
    validation_verbose: Option<bool>,
) -> PyResult<String> {
    let mut processor = XacroProcessor::new(verbosity.unwrap_or(1));
    processor.set_format_output(format_output.unwrap_or(true)); // Format output by default
    processor.set_remove_root_link(remove_root_link.map(|s| s.to_string()));
    processor.set_validate_urdf(validate_urdf.unwrap_or(true)); // Validation enabled by default
    processor.set_validation_verbose(validation_verbose.unwrap_or(true));

    let mappings = if let Some(dict) = mappings {
        let mut map = HashMap::new();
        for (key, value) in dict {
            let key: String = key.extract()?;
            let value: String = value.extract()?;
            map.insert(key, value);
        }
        Some(map)
    } else {
        None
    };

    match processor.process_string(xml_content, mappings) {
        Ok(doc) => Ok(processor.element_to_string(&doc)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_to_file(
    input_file: &str,
    output_file: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_root_link: Option<&str>,
    validate_urdf: Option<bool>,
    validation_verbose: Option<bool>,
) -> PyResult<()> {
    let result = xacro_to_string(
        input_file,
        mappings,
        verbosity,
        format_output,
        remove_root_link,
        validate_urdf,
        validation_verbose,
    )?;

    // Create output directory if needed
    if let Some(parent) = Path::new(output_file).parent() {
        std::fs::create_dir_all(parent).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to create directory: {}", e))
        })?;
    }

    std::fs::write(output_file, result).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to write file: {}", e))
    })?;

    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
fn validate_urdf_rust(urdf_content: &str, verbose: Option<bool>) -> PyResult<(bool, Vec<String>)> {
    use crate::urdf_validator::validate_urdf;

    match validate_urdf(urdf_content, verbose.unwrap_or(true)) {
        Ok(result) => Ok((result.is_valid, result.errors)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
            "Validation error: {}",
            e
        ))),
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn print_urdf_tree_rust(urdf_content: &str) -> PyResult<String> {
    use crate::urdf_validator::print_urdf_tree;

    match print_urdf_tree(urdf_content) {
        Ok(tree) => Ok(tree),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
            "Tree generation error: {}",
            e
        ))),
    }
}

#[cfg(feature = "python")]
#[pymodule]
fn zacro(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyXacroProcessor>()?;
    m.add_function(wrap_pyfunction!(xacro_to_string, m)?)?;
    m.add_function(wrap_pyfunction!(xacro_from_string, m)?)?;
    m.add_function(wrap_pyfunction!(xacro_to_file, m)?)?;
    m.add_function(wrap_pyfunction!(validate_urdf_rust, m)?)?;
    m.add_function(wrap_pyfunction!(print_urdf_tree_rust, m)?)?;
    Ok(())
}
