use super::base::{convert_to_nested_edit_distance_item_vec, convert_to_edit_distance_vec, EditDistanceItem};
use crate::core;
use pyo3::types::PyList;
use pyo3::{pyfunction, Bound, PyAny, PyResult};

#[pyfunction(name = "poi_edit_distance")]
pub fn poi_edit_distance_py(
    predictions: Vec<Bound<PyAny>>,
    references: Vec<Bound<PyAny>>,
    points_of_interest: Vec<bool>,
) -> PyResult<usize> {
    let pred: Vec<EditDistanceItem> = convert_to_edit_distance_vec(&predictions)?;
    let ref_: Vec<EditDistanceItem> = convert_to_edit_distance_vec(&references)?;

    let result = core::pier::poi_edit_distance(&pred, &ref_, &points_of_interest);
    Ok(result)
}

#[pyfunction(name = "poi_error_rate")]
pub fn poi_error_rate_py(
    predictions: &Bound<PyList>,
    references: &Bound<PyList>,
    points_of_interest: Vec<Vec<bool>>,
) -> PyResult<f64> {
    // Create vectors to store the converted data
    let pred_vecs: Vec<Vec<EditDistanceItem>> = convert_to_nested_edit_distance_item_vec(predictions)?;
    let ref_vecs: Vec<Vec<EditDistanceItem>> = convert_to_nested_edit_distance_item_vec(references)?;

    // Create the vectors of references to vectors that the edit_distance function expects
    let pred_vec_refs: Vec<&[EditDistanceItem]> = pred_vecs.iter().map(|v| v.as_slice()).collect();
    let ref_vec_refs: Vec<&[EditDistanceItem]> = ref_vecs.iter().map(|v| v.as_slice()).collect();
    let poi_vec_refs: Vec<&[bool]> = points_of_interest.iter().map(|v| v.as_slice()).collect();

    // Call a modified edit_distance implementation that works with EditDistanceItem
    let result = core::pier::poi_error_rate(&pred_vec_refs, &ref_vec_refs, &poi_vec_refs);

    Ok(result)
}
