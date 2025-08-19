use pyo3::prelude::*;

mod bindings;
mod core;

use bindings::*;

/// A Python module implemented in Rust.
#[pymodule]
fn universal_edit_distance(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Character error rate
    m.add_function(wrap_pyfunction!(cer::character_edit_distance_array_py, m)?)?;
    m.add_function(wrap_pyfunction!(cer::character_error_rate_py, m)?)?;
    m.add_function(wrap_pyfunction!(cer::character_error_rate_array_py, m)?)?;

    // Optimal alignment
    m.add_function(wrap_pyfunction!(alignment::optimial_alignment_py, m)?)?;
    m.add_class::<core::alignment::Alignment>()?;

    // Points of interest error rate
    m.add_function(wrap_pyfunction!(pier::poi_edit_distance_py, m)?)?;
    m.add_function(wrap_pyfunction!(pier::poi_error_rate_py, m)?)?;

    // Universal error rate
    m.add_function(wrap_pyfunction!(uer::universal_edit_distance_array_py, m)?)?;
    m.add_function(wrap_pyfunction!(uer::universal_error_rate_array_py, m)?)?;

    // Word error rate
    m.add_function(wrap_pyfunction!(wer::word_edit_distance_array_py, m)?)?;
    m.add_function(wrap_pyfunction!(wer::word_error_rate_py, m)?)?;
    m.add_function(wrap_pyfunction!(wer::word_error_rate_array_py, m)?)?;

    Ok(())
}
