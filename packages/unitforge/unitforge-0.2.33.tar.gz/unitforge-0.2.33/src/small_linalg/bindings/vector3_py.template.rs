use std::mem::discriminant;
use pyo3::{exceptions::PyValueError, types::PyList};
use numpy::{PyReadonlyArray1, PyArray1};
use crate::small_linalg::Vector3;

#[pyclass(eq)]
#[derive(PartialEq, Clone)]
#[pyo3(name = "Vector3")]
pub struct Vector3Py {
    pub data: [Quantity; 3]
}

impl Vector3Py {
    pub fn from_raw_float(raw: Vector3<f64>) -> Self {
        Self {
            data: [Quantity::FloatQuantity(raw[0]), Quantity::FloatQuantity(raw[1]), Quantity::FloatQuantity(raw[2])]
        }
    }

    pub fn into_raw_float(self) -> Result<Vector3<f64>, String> {
        if discriminant(&self.data[0]) != discriminant(&Quantity::FloatQuantity(0.0)) {
            Err("Cannot convert Vector3Py into Vector3 with other contained type".to_string())
        }
        else {
            Ok(Vector3::new([self.data[0].extract_float()?, self.data[1].extract_float()?, self.data[2].extract_float()?]))
        }
    }

    //__RAW_INTERFACE__
}

impl Vector3Py {
    pub fn format(&self) -> String {
        format!(
            "Vector3: [{:?}, {:?}, {:?}]",
            self.data[0],
            self.data[1],
            self.data[2]
        )
    }
}

#[pymethods]
impl Vector3Py {
    #[new]
    #[pyo3(signature = (x, y, z, unit=None))]
    fn new(x: &Bound<PyAny>, y: &Bound<PyAny>, z: &Bound<PyAny>, unit: Option<&Bound<PyAny>>) -> PyResult<Self> {
        match unit {
            Some(unit_py) => {
                let unit = Unit::from_py_any(unit_py).map_err(|e| PyValueError::new_err(e.to_string()))?;
                let values = [x.extract::<f64>().map_err(|_| {
                    PyValueError::new_err("x element is not a number".to_string())
                })?,
                y.extract::<f64>().map_err(|_| {
                    PyValueError::new_err("y element is not a number".to_string())
                })?,
                z.extract::<f64>().map_err(|_| {
                    PyValueError::new_err("z element is not a number".to_string())
                })?];

                Ok(Vector3Py{
                    data: [unit.to_quantity(values[0]),
                            unit.to_quantity(values[1]),
                            unit.to_quantity(values[2])]
                })
            }
            None => {
                let x_quantity = Quantity::from_py_any(x).map_err(|e| PyValueError::new_err(e.to_string()))?;
                let y_quantity = Quantity::from_py_any(y).map_err(|e| PyValueError::new_err(e.to_string()))?;
                let z_quantity = Quantity::from_py_any(z).map_err(|e| PyValueError::new_err(e.to_string()))?;
                if discriminant(&x_quantity) != discriminant(&y_quantity) || discriminant(&x_quantity) != discriminant(&z_quantity) {
                    return Err(PyValueError::new_err("The passed values must be of the same quantity.".to_string()));
                }
                Ok(Vector3Py {
                    data: [x_quantity, y_quantity, z_quantity],
                })
            }
        }
    }

    #[staticmethod]
    fn zero() -> Self {
        Vector3Py {
            data: [Quantity::FloatQuantity(0.); 3]
        }
    }

    #[staticmethod]
    fn x() -> Self {
        Vector3Py {
            data: [Quantity::FloatQuantity(1.), Quantity::FloatQuantity(0.), Quantity::FloatQuantity(0.)]
        }
    }

    #[staticmethod]
    fn y() -> Self {
        Vector3Py {
            data: [Quantity::FloatQuantity(0.), Quantity::FloatQuantity(1.), Quantity::FloatQuantity(0.)]
        }
    }

    #[staticmethod]
    fn z() -> Self {
        Vector3Py {
            data: [Quantity::FloatQuantity(0.), Quantity::FloatQuantity(0.), Quantity::FloatQuantity(1.)]
        }
    }

    fn __getitem__(&self, py: Python, index: usize) -> PyResult<PyObject> {
        Ok(self.data[index].to_pyobject(py))
    }

    fn __setitem__(&mut self, index: usize, value: &Bound<PyAny>) -> PyResult<()> {
        let value_quantity = Quantity::from_py_any(value).map_err(|e| PyValueError::new_err(e.to_string()))?;
        for item in &mut self.data {
            if discriminant(item) != discriminant(&value_quantity) {
                return Err(PyValueError::new_err("The passed values must be of the same quantity as the Vector3.".to_string()));
            }
        }
        self.data[index] = value_quantity;
        Ok(())
    }

    fn __add__(&self, other: &Vector3Py) -> PyResult<Self> {
        if discriminant(&self.data[0]) != discriminant(&other.data[0]) {
            Err(PyValueError::new_err("The passed values must be of the same quantity.".to_string()))
        } else {
            Ok(Vector3Py {
                data: [self.data[0].add(other.data[0]).unwrap(),
                    self.data[1].add(other.data[1]).unwrap(),
                    self.data[2].add(other.data[2]).unwrap()]
            })
        }
    }

    fn __sub__(&self, other: &Vector3Py) -> PyResult<Self> {
        if discriminant(&self.data[0]) != discriminant(&other.data[0]) {
            Err(PyValueError::new_err("The passed values must be of the same quantity.".to_string()))
        } else {
            Ok(Vector3Py {
                data: [self.data[0].sub(other.data[0]).unwrap(),
                    self.data[1].sub(other.data[1]).unwrap(),
                    self.data[2].sub(other.data[2]).unwrap()]
            })
        }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(self.format())
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(self.format())
    }

    fn to_list<'p>(&self, py: Python<'p>) -> PyResult<Bound<'p, PyList>> {
        let list = PyList::empty_bound(py);
        list.append(self.data[0].to_pyobject(py))?;
        list.append(self.data[1].to_pyobject(py))?;
        list.append(self.data[2].to_pyobject(py))?;
        Ok(list)
    }

    #[staticmethod]
    #[pyo3(signature = (lst, unit=None))]
    fn from_list(lst: Bound<PyList>, unit: Option<&Bound<PyAny>>) -> PyResult<Self> {
        if lst.len() != 3 {
            return Err(PyValueError::new_err(
                "List must contain exactly 3 elements",
            ));
        }
        match unit {
            Some(unit_py) => {
                let unit = Unit::from_py_any(unit_py).map_err(|e| PyValueError::new_err(e.to_string()))?;
                let mut values = [0.; 3];
                for (i, elem) in lst.iter().enumerate() {
                    values[i] = elem.extract::<f64>().map_err(|_| {
                        PyValueError::new_err(format!("Element at index {i} is not a number"))
                    })?;
                }
                Ok(Vector3Py{
                    data: [
                        unit.to_quantity(values[0]),
                        unit.to_quantity(values[1]),
                        unit.to_quantity(values[2]),
                    ]
                })
            }
            None => {
                let mut data = [Quantity::FloatQuantity(0.); 3];
                for (i, elem) in lst.iter().enumerate() {
                    data[i] = Quantity::from_py_any(&elem).map_err(|e| PyValueError::new_err(e.to_string()))?;
                }
                if discriminant(&data[0]) != discriminant(&data[1]) || discriminant(&data[0]) != discriminant(&data[2]) {
                    Err(PyValueError::new_err("The passed values must be of the same quantity.".to_string()))
                }
                else {
                    Ok(
                        Vector3Py {
                            data
                        }
                    )
                }
            }
        }
    }

    #[staticmethod]
    fn from_array(array: PyReadonlyArray1<f64>, unit: &Bound<PyAny>) -> PyResult<Self> {
        match array.as_slice() {
            Err(_) => Err(PyValueError::new_err("Failed to convert array to vector")),
            Ok(values) => {
                if values.len() != 3 {
                    return Err(PyValueError::new_err("Array must contain exactly 3 elements"))
                }
                let extracted_unit = Unit::from_py_any(unit).map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Vector3Py{
                    data: [
                        extracted_unit.to_quantity(values[0]),
                        extracted_unit.to_quantity(values[1]),
                        extracted_unit.to_quantity(values[2]),
                    ]
                })
            }
        }
    }

    fn to_array(&self, py: Python, unit: &Bound<PyAny>) -> PyResult<PyObject> {
        let extracted_unit = Unit::from_py_any(unit).map_err(|e| PyValueError::new_err(e.to_string()))?;
        let mut v = Vec::with_capacity(3);
        for elem in self.data {
            v.push(elem.to(extracted_unit).map_err(|e| PyValueError::new_err(e.to_string()))?);
        }
        Ok(PyArray1::from_vec_bound(py, v).into_py(py))
    }

    fn norm(&self, py: Python) -> PyResult<PyObject> {
        fn rust_norm(data: &[Quantity; 3]) -> Result<Quantity, QuantityOperationError> {
            let mut products = Vec::with_capacity(3);
            for item in data {
                products.push((*item * *item)?);
            }
            let sum = (products[0] + products[1])? + products[2];
            sum?.sqrt()
        }
        rust_norm(&self.data)
            .map_err(|_| PyValueError::new_err("Failed to compute norm"))
            .map(|norm_value| norm_value.to_pyobject(py))
    }

    fn to_unit_vector(&self, py: Python) -> Self {
        let norm = self.norm(py).unwrap();
        let norm_bound = norm.bind(py);
        let norm_quantity = Quantity::from_py_any(norm_bound).unwrap();
        Vector3Py {
            data: [
                (self.data[0] / norm_quantity).unwrap(),
                (self.data[1] / norm_quantity).unwrap(),
                 (self.data[2] / norm_quantity).unwrap(),
            ]
        }
    }

    fn dot_vec(&self, py: Python, other: Vector3Py) -> PyResult<PyObject> {
        fn rust_dot_vec(data_lhs: &[Quantity; 3], data_rhs: &[Quantity; 3]) -> Result<Quantity, QuantityOperationError> {
            let mut products = Vec::with_capacity(3);
            for i in 0..3 {
                products.push((data_lhs[i] * data_rhs[i])?);
            }
            (products[0] + products[1])? + products[2]
        }
        rust_dot_vec(&self.data, &other.data)
            .map_err(|_| PyValueError::new_err("Failed to compute dot_vec"))
            .map(|norm_value| norm_value.to_pyobject(py))
    }

    fn cross(&self, other: Vector3Py) -> PyResult<Vector3Py> {
        fn rust_cross(data_lhs: &[Quantity; 3], data_rhs: &[Quantity; 3]) -> Result<[Quantity; 3], QuantityOperationError> {
            Ok([((data_lhs[1] * data_rhs[2])? - (data_lhs[2] * data_rhs[1])?)?,
                ((data_lhs[2] * data_rhs[0])? - (data_lhs[0] * data_rhs[2])?)?,
                ((data_lhs[0] * data_rhs[1])? - (data_lhs[1] * data_rhs[0])?)?])
        }
        match rust_cross(&self.data, &other.data) {
            Ok(res_data) => Ok(Vector3Py { data: res_data }),
            Err(_) => Err(PyValueError::new_err("Failed to compute cross"))
        }
    }

    fn __mul__(&self, py: Python, rhs: Py<PyAny>) -> PyResult<Self> {
        let rhs_ref = rhs.bind(py);
        let rhs_quantity = Quantity::from_py_any(rhs_ref)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Vector3Py { data: [
            (self.data[0] * rhs_quantity).map_err(|_| PyValueError::new_err("Cannot multiply given Quantities."))?,
            (self.data[1] * rhs_quantity).map_err(|_| PyValueError::new_err("Cannot multiply given Quantities."))?,
            (self.data[2] * rhs_quantity).map_err(|_| PyValueError::new_err("Cannot multiply given Quantities."))?] })
    }

    fn __truediv__(&self, py: Python, rhs: Py<PyAny>) -> PyResult<Self> {
        let rhs_ref = rhs.bind(py);
        let rhs_quantity = Quantity::from_py_any(rhs_ref)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Vector3Py { data: [
            (self.data[0] / rhs_quantity).map_err(|_| PyValueError::new_err("Cannot divide given Quantities."))?,
            (self.data[1] / rhs_quantity).map_err(|_| PyValueError::new_err("Cannot divide given Quantities."))?,
            (self.data[2] / rhs_quantity).map_err(|_| PyValueError::new_err("Cannot divide given Quantities."))?] })
    }
}