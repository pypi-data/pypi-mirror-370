use numpy::{PyReadonlyArray2, PyArray2};
use num_traits::Zero;
use crate::small_linalg::Matrix3;

#[pyclass(eq)]
#[derive(PartialEq)]
#[pyo3(name = "Matrix3")]
pub struct Matrix3Py {
    pub data: [[Quantity; 3]; 3]
}

impl Matrix3Py {
    pub fn from_raw_float(raw: Matrix3<f64>) -> Self {
        Self {
            data: [[Quantity::FloatQuantity(raw[(0, 0)]), Quantity::FloatQuantity(raw[(0, 1)]), Quantity::FloatQuantity(raw[(0, 2)])],
                [Quantity::FloatQuantity(raw[(1, 0)]), Quantity::FloatQuantity(raw[(1, 1)]), Quantity::FloatQuantity(raw[(1, 2)])],
                [Quantity::FloatQuantity(raw[(2, 0)]), Quantity::FloatQuantity(raw[(2, 1)]), Quantity::FloatQuantity(raw[(2, 2)])],
            ]
        }
    }

    pub fn into_raw_float(self) -> Result<Matrix3<f64>, String> {
        if discriminant(&self.data[0][0]) != discriminant(&Quantity::FloatQuantity(0.0)) {
            Err("Cannot convert Matrix3Py into Matrix3 with other contained type".to_string())
        }
        else {
            Ok(Matrix3::new([[self.data[0][0].extract_float()?, self.data[0][1].extract_float()?, self.data[0][2].extract_float()?],
                [self.data[1][0].extract_float()?, self.data[1][1].extract_float()?, self.data[1][2].extract_float()?],
                [self.data[2][0].extract_float()?, self.data[2][1].extract_float()?, self.data[2][2].extract_float()?]]))
        }
    }

    //__RAW_INTERFACE__
}

#[pymethods]
impl Matrix3Py {
    #[new]
    #[pyo3(signature = (data=None, unit=None))]
    fn new(
        data: Option<&Bound<PyAny>>,
        unit: Option<&Bound<PyAny>>,
    ) -> PyResult<Self> {
        use pyo3::exceptions::PyValueError;
        match data {
            None => Ok(Self::zero()),
            Some(obj) => {
                if let Ok(lst) = obj.extract::<Bound<PyList>>() {
                    Self::from_list(lst, unit)
                }
                else if let Ok(array) = obj.extract::<PyReadonlyArray2<f64>>() {
                    Self::from_array(array, unit)
                }
                else {
                    Err(PyValueError::new_err("Only a List of lists or a numpy array may be passed as first argument"))
                }
            }
        }
    }

    #[staticmethod]
    pub fn zero() -> Self {
        Matrix3Py {
            data: [[Quantity::FloatQuantity(0.); 3]; 3]
        }
    }

    fn __getitem__(&self, py: Python, indices: (usize, usize)) -> PyResult<PyObject> {
        Ok(self.data[indices.0][indices.1].to_pyobject(py))
    }

    fn __setitem__(&mut self, indices: (usize, usize), value: &Bound<PyAny>) -> PyResult<()> {
        let value_quantity = Quantity::from_py_any(value).map_err(|e| PyValueError::new_err(e.to_string()))?;
        for row in &mut self.data {
            for item in row {
                if discriminant(item) != discriminant(&value_quantity) {
                    return Err(PyValueError::new_err("The passed values must be of the same quantity as the Matrix3.".to_string()));
                }
            }
        }
        self.data[indices.0][indices.1] = value_quantity;
        Ok(())
    }

    #[staticmethod]
    fn identity() -> Self {
        let mut data = [[Quantity::FloatQuantity(0.); 3]; 3];
        data[0][0] = Quantity::FloatQuantity(1.);
        data[1][1] = Quantity::FloatQuantity(1.);
        data[2][2] = Quantity::FloatQuantity(1.);
        Matrix3Py {
            data
        }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(self.format())
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.format())
    }

    #[staticmethod]
    #[pyo3(signature = (lst, unit=None))]
    fn from_list(lst: Bound<PyList>, unit: Option<&Bound<PyAny>>) -> PyResult<Self> {
        if lst.len() != 3 {
            return Err(PyValueError::new_err(
                "List must contain exactly 3 elements",
            ));
        }

        for row in lst.iter() {
            let sublist = row.downcast::<PyList>()?;
            if sublist.len() != 3 {
                return Err(PyValueError::new_err(
                    "Each sub list must contain exactly 3 elements",
                ));
            }
        }
        let rust_unit = match unit {
            Some(py_unit) => {
                Unit::from_py_any(py_unit).map_err(|e| PyValueError::new_err(e.to_string()))?
            }
            None => {
                Unit::NoUnit
            }
        };
        let mut data = [[Quantity::FloatQuantity(0.0); 3]; 3];
        for (i, row) in lst.iter().enumerate() {
            let sublist = row
                .downcast::<PyList>()
                .map_err(|_| PyValueError::new_err(format!("Row {i} is not a list")))?;

            for (j, elem) in sublist.iter().enumerate() {
                let val = elem
                    .extract::<f64>()
                    .map_err(|_| {
                        PyValueError::new_err(format!(
                            "Element at row {i} column {j} is not convertible to float"
                        ))
                    })?;
                data[i][j] = rust_unit.to_quantity(val)
            }
        }
        Ok(Matrix3Py {
            data
        })
    }

    #[pyo3(signature = (unit=None))]
    fn to_list<'p>(&self, py: Python<'p>, unit: Option<&Bound<PyAny>>) -> PyResult<Bound<'p, PyList>> {
        let list = PyList::empty_bound(py);
        for i in 0..3 {
            let row = PyList::empty_bound(py);
            for j in 0..3 {
                match unit {
                    None => row.append(self.data[i][j].to_pyobject(py))?,
                    Some(unit_py) => {
                        let unit = Unit::from_py_any(unit_py).map_err(|e| PyValueError::new_err(e.to_string()))?;
                        row.append(self.data[i][j].to(unit).map_err(|e| PyValueError::new_err(e.to_string()))?)?
                    },
                }
            }
            list.append(row)?;
        }
        Ok(list)
    }

    #[staticmethod]
    #[pyo3(signature = (array, unit=None))]
    fn from_array(array: PyReadonlyArray2<f64>, unit: Option<&Bound<PyAny>>) -> PyResult<Self> {
        let flat: &[f64] = array
            .as_slice()
            .map_err(|_| PyValueError::new_err("Failed to convert array to matrix"))?;

        if flat.len() != 9 {
            return Err(PyValueError::new_err(
                "Array must contain exactly 3×3 = 9 elements",
            ));
        }

        let rust_unit = match unit {
            Some(py_unit) => {
                Unit::from_py_any(py_unit).map_err(|e| PyValueError::new_err(e.to_string()))?
            }
            None => {
                Unit::NoUnit
            }
        };

        let mut data = [[Quantity::FloatQuantity(0.0); 3]; 3];
        for (index, value) in flat.iter().enumerate().take(9) {
            let row = index / 3;
            let col = index % 3;
            data[row][col] = rust_unit.to_quantity(*value);
        }
        Ok(Matrix3Py { data })
    }

    fn to_array(&self, py: Python, unit: &Bound<PyAny>) -> PyResult<Py<PyArray2<f64>>> {
        let rust_unit = Unit::from_py_any(unit)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        let mut flat_data = Vec::with_capacity(9);
        for i in 0..3 {
            for j in 0..3 {
                flat_data.push(self.data[i][j].to(rust_unit).map_err(|e| PyValueError::new_err(e.to_string()))?);
            }
        }
        let array2 = ndarray::Array2::from_shape_vec((3, 3), flat_data)
            .map_err(|e| PyValueError::new_err(format!("Error creating ndarray array: {e}")))?;
        Ok(PyArray2::from_owned_array_bound(py, array2).into())
    }

    #[staticmethod]
    fn from_rows(rows: Bound<PyList>) -> PyResult<Self> {
        if rows.len() != 3 {
            return Err(PyValueError::new_err(
                "List must contain exactly 3 elements",
            ));
        }
        let mut rows_unpacked = [Vector3Py::zero(), Vector3Py::zero(), Vector3Py::zero()];
        for (i, elem) in rows.iter().enumerate() {
            rows_unpacked[i] = elem.extract::<Vector3Py>().map_err(|_| {
                PyValueError::new_err(format!("Element at index {i} is a Vector3"))
            })?;
        }
        if discriminant(&rows_unpacked[0].data[0]) != discriminant(&rows_unpacked[1].data[0]) ||
            discriminant(&rows_unpacked[0].data[0]) != discriminant(&rows_unpacked[2].data[0]) {
            return Err(PyValueError::new_err(
                "All vectors must have the same Quantity.",
            ));
        }
        Ok(Self {
            data: [[rows_unpacked[0].data[0], rows_unpacked[0].data[1], rows_unpacked[0].data[2]],
                [rows_unpacked[1].data[0], rows_unpacked[1].data[1], rows_unpacked[1].data[2]],
                [rows_unpacked[2].data[0], rows_unpacked[2].data[1], rows_unpacked[2].data[2]]],
        })
    }

    #[staticmethod]
    fn from_columns(columns: Bound<PyList>) -> PyResult<Self> {
        Ok(Self::from_rows(columns)?.transpose())
    }

    fn transpose(&self) -> Self {
        Self {
            data: [[self.data[0][0], self.data[1][0], self.data[2][0]],
                [self.data[0][1], self.data[1][1], self.data[2][1]],
                [self.data[0][2], self.data[1][2], self.data[2][2]]],
        }
    }

    fn get_column(&self, index: usize) -> PyResult<Vector3Py> {
        if index >= 3 {
            return Err(PyValueError::new_err("Index must be 0, 1 or 2"));
        }
        Ok(Vector3Py {
            data: [
                self.data[0][index],
                self.data[1][index],
                self.data[2][index],
            ],
        })
    }

    fn set_column(&mut self, index: usize, value: Vector3Py) -> PyResult<()>{
        if index >= 3 {
            return Err(PyValueError::new_err("Index must be 0, 1 or 2"));
        }
        for i in 0..3 {
            self.data[i][index] = value.data[i];
        }
        Ok(())
    }

    fn get_row(&self, index: usize) -> PyResult<Vector3Py> {
        if index >= 3 {
            return Err(PyValueError::new_err("Index must be 0, 1 or 2"));
        }
        Ok(Vector3Py {
            data: [
                self.data[index][0],
                self.data[index][1],
                self.data[index][2],
            ],
        })
    }

    fn set_row(&mut self, index: usize, value: Vector3Py) -> PyResult<()> {
        if index >= 3 {
            return Err(PyValueError::new_err("Index must be 0, 1 or 2"));
        }
        self.data[index].copy_from_slice(&value.data);
        Ok(())
    }
}

impl Matrix3Py {
    pub fn format(&self) -> String {
        format!(
            "Matrix3: [\n[{:?}, {:?}, {:?}]\n[{:?}, {:?}, {:?}]\n[{:?}, {:?}, {:?}]]",
            self.data[0][0],
            self.data[0][1],
            self.data[0][2],
            self.data[1][0],
            self.data[1][1],
            self.data[1][2],
            self.data[2][0],
            self.data[2][1],
            self.data[2][2],
        )
    }
}
