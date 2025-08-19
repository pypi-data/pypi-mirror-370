use crate::core;
use pyo3::{pyfunction, PyResult};

#[pyfunction(name = "character_error_rate_array")]
pub fn character_error_rate_array_py(
    predictions: Vec<String>,
    references: Vec<String>,
) -> PyResult<Vec<f64>> {
    let left_vec: Vec<&str> = predictions.iter().map(|x| x.as_str()).collect();
    let right_vec: Vec<&str> = references.iter().map(|x| x.as_str()).collect();
    let result = core::cer::character_error_rate_array(&left_vec, &right_vec);
    Ok(result)
}

#[pyfunction(name = "character_edit_distance_array")]
pub fn character_edit_distance_array_py(
    predictions: Vec<String>,
    references: Vec<String>,
) -> PyResult<Vec<usize>> {
    let left_vec: Vec<&str> = predictions.iter().map(|x| x.as_str()).collect();
    let right_vec: Vec<&str> = references.iter().map(|x| x.as_str()).collect();
    let result = core::cer::character_edit_distance_array(&left_vec, &right_vec);
    Ok(result)
}

#[pyfunction(name = "character_error_rate")]
pub fn character_error_rate_py(predictions: Vec<String>, references: Vec<String>) -> PyResult<f64> {
    let left_vec: Vec<&str> = predictions.iter().map(|x| x.as_str()).collect();
    let right_vec: Vec<&str> = references.iter().map(|x| x.as_str()).collect();
    let result = core::cer::character_error_rate(&left_vec, &right_vec);
    Ok(result)
}
