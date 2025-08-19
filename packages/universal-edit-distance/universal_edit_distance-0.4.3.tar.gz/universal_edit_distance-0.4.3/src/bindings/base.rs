use pyo3::{
    types::{PyAnyMethods, PyList},
    Bound, FromPyObject, IntoPyObjectExt, Py, PyAny, PyResult, Python,
};

#[derive(Debug)]
pub enum EditDistanceItem {
    String(String),
    Int(i64),
    Float(f64),
    Bool(bool),
    Object(Py<PyAny>),
}

impl PartialEq for EditDistanceItem {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (EditDistanceItem::String(a), EditDistanceItem::String(b)) => a == b,
            (EditDistanceItem::Int(a), EditDistanceItem::Int(b)) => a == b,
            (EditDistanceItem::Float(a), EditDistanceItem::Float(b)) => a == b,
            (EditDistanceItem::Bool(a), EditDistanceItem::Bool(b)) => a == b,
            (EditDistanceItem::Object(a), EditDistanceItem::Object(b)) => {
                // Use Python's __eq__ by acquiring the GIL
                Python::with_gil(|py| {
                    // Bind the Py<PyAny> to this thread-local context
                    let a_bound = a.bind(py);
                    let b_bound = b.bind(py);
                    a_bound.eq(&b_bound).unwrap_or(false)
                })
            }
            // If types don't match, defer to Python's eq function
            (a, b) => Python::with_gil(|py| {
                let to_py = |item: &EditDistanceItem| -> Option<Py<PyAny>> {
                    match item {
                        EditDistanceItem::String(s) => s.into_py_any(py).ok(),
                        EditDistanceItem::Int(i) => i.into_py_any(py).ok(),
                        EditDistanceItem::Float(f) => f.into_py_any(py).ok(),
                        EditDistanceItem::Bool(b) => b.into_py_any(py).ok(),
                        EditDistanceItem::Object(obj) => Some(obj.clone_ref(py)),
                    }
                };

                match (to_py(a), to_py(b)) {
                    // if both are fine, defer to Python, otherwise assume False
                    (Some(a), Some(b)) => a.bind(py).eq(b.bind(py)).unwrap_or(false),
                    _ => false,
                }
            }),
        }
    }
}

impl<'source> FromPyObject<'source> for EditDistanceItem {
    fn extract_bound(obj: &Bound<'source, PyAny>) -> PyResult<Self> {
        // Try to extract each supported type in order
        if let Ok(val) = obj.extract::<String>() {
            return Ok(EditDistanceItem::String(val));
        } else if let Ok(val) = obj.extract::<i64>() {
            return Ok(EditDistanceItem::Int(val));
        } else if let Ok(val) = obj.extract::<f64>() {
            return Ok(EditDistanceItem::Float(val));
        } else if let Ok(val) = obj.extract::<bool>() {
            return Ok(EditDistanceItem::Bool(val));
        } else {
            // For any other type, store the Python object for later comparison
            let py_obj = obj.clone().unbind();
            return Ok(EditDistanceItem::Object(py_obj));
        }
    }
}

pub(crate) fn convert_to_edit_distance_vec(
    items: &Vec<Bound<PyAny>>,
) -> PyResult<Vec<EditDistanceItem>> {
    items
        .into_iter()
        .map(|item| item.extract::<EditDistanceItem>())
        .collect()
}

pub fn convert_to_nested_edit_distance_item_vec(
    pylist: &Bound<PyList>,
) -> PyResult<Vec<Vec<EditDistanceItem>>> {
    // Create vectors to store the converted data
    let mut vecs: Vec<Vec<EditDistanceItem>> = Vec::with_capacity(pylist.len()?);

    // Extract the data from Python
    for i in 0..pylist.len()? {
        let item = pylist.get_item(i)?;
        let list = item.downcast::<PyList>()?;

        let mut inner: Vec<EditDistanceItem> = Vec::with_capacity(list.len()?);

        // Extract items from the inner lists, converting to EditDistanceItem
        for j in 0..list.len()? {
            inner.push(list.get_item(j)?.extract::<EditDistanceItem>()?);
        }

        vecs.push(inner);
    }

    // Create the vectors of references to vectors that the edit_distance function expects
    return Ok(vecs);
}
