use crate::core;
use pyo3::{pyfunction, Bound, PyAny, PyResult};

use super::base::{convert_to_edit_distance_vec, EditDistanceItem};

#[pyfunction(name = "optimal_alignment")]
pub fn optimial_alignment_py(
    predictions: Vec<Bound<PyAny>>,
    references: Vec<Bound<PyAny>>,
) -> PyResult<Vec<core::alignment::Alignment>> {
    let pred: Vec<EditDistanceItem> = convert_to_edit_distance_vec(&predictions)?;
    let ref_: Vec<EditDistanceItem> = convert_to_edit_distance_vec(&references)?;

    let result = core::alignment::optimial_aligment(&pred, &ref_);
    Ok(result)
}
