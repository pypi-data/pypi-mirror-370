#[macro_export]
macro_rules! impl_quantity {
    ($type:ident, $unit:ty, $display_unit:expr) => {
        #[cfg(feature = "pyo3")]
        use pyo3::{
            basic::CompareOp, exceptions::PyValueError, pymethods, types::PyType, Bound, IntoPy,
            Py, PyAny, PyObject, PyRef, PyResult,
        };
        use $crate::small_linalg::{Matrix3, Vector3};
        #[cfg(feature = "pyo3")]
        use $crate::Quantity;

        #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
        #[cfg(feature = "pyo3")]
        #[pyclass]
        #[derive(Copy, Clone)]
        pub struct $type {
            pub(crate) multiplier: f64,
            pub(crate) power: i32,
        }
        #[cfg(not(feature = "pyo3"))]
        #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
        #[derive(Copy, Clone)]
        pub struct $type {
            pub(crate) multiplier: f64,
            pub(crate) power: i32,
        }

        impl PhysicsQuantity for $type {
            fn as_f64(&self) -> f64 {
                self.multiplier * 10_f64.powi(self.power)
            }

            type Unit = $unit;

            fn new(value: f64, unit: Self::Unit) -> $type {
                if value.is_infinite() {
                    if value.is_sign_negative() {
                        return Self::NEG_INFINITY;
                    } else {
                        return Self::INFINITY;
                    }
                }
                if value.is_zero() {
                    return $type {
                        multiplier: 0.0,
                        power: 0,
                    };
                }
                let (unit_multiplier, unit_power) = unit.base_per_x();
                let (multiplier, power) = Self::split_value(value);
                let r = $type {
                    multiplier: multiplier * unit_multiplier,
                    power: power + unit_power,
                };
                r
            }

            fn split_value(v: f64) -> (f64, i32) {
                if v.is_zero() {
                    (0.0, 0)
                } else {
                    let power = v.abs().log10().floor() as i32;
                    let multiplier = v / 10f64.powi(power);
                    (multiplier, power)
                }
            }

            fn get_value(&self) -> f64 {
                self.multiplier * 10_f64.powi(self.power)
            }

            fn get_power(&self) -> i32 {
                self.power
            }

            fn get_multiplier(&self) -> f64 {
                self.multiplier
            }

            fn get_tuple(&self) -> (f64, i32) {
                (self.multiplier, self.power)
            }

            fn to(&self, unit: Self::Unit) -> f64 {
                let (unit_multiplier, unit_power) = unit.base_per_x();
                self.multiplier / unit_multiplier * 10_f64.powi(self.power - unit_power)
            }

            fn abs(self) -> Self {
                Self {
                    multiplier: self.multiplier.abs(),
                    power: self.power,
                }
            }

            fn is_nan(&self) -> bool {
                self.multiplier.is_nan()
            }

            fn from_raw(value: f64) -> Self {
                if value.is_infinite() {
                    if value.is_sign_negative() {
                        return Self::NEG_INFINITY;
                    } else {
                        return Self::INFINITY;
                    }
                }
                let (multiplier, power) = Self::split_value(value);
                Self { multiplier, power }
            }

            fn from_exponential(multiplier: f64, power: i32) -> Self {
                Self { multiplier, power }
            }

            fn min(self, other: Self) -> Self {
                if self < other {
                    self
                } else {
                    other
                }
            }

            fn max(self, other: Self) -> Self {
                if self > other {
                    self
                } else {
                    other
                }
            }

            fn is_close(&self, other: &Self, tolerance: &Self) -> bool {
                (self.as_f64() - other.as_f64()).abs() <= tolerance.as_f64().abs()
            }

            fn optimize(&mut self) {
                if self.multiplier.abs() < f64::EPSILON {
                    return;
                }
                let power_on_multiplier = self.multiplier.abs().log10().round() as i32;
                self.multiplier /= 10_f64.powi(power_on_multiplier);
                self.power += power_on_multiplier;
            }

            const INFINITY: Self = Self {
                multiplier: f64::INFINITY,
                power: 0,
            };

            const NEG_INFINITY: Self = Self {
                multiplier: f64::NEG_INFINITY,
                power: 0,
            };
        }

        impl From<f64> for $type {
            fn from(value: f64) -> Self {
                if value.is_infinite() {
                    if value.is_sign_negative() {
                        return Self::NEG_INFINITY;
                    } else {
                        return Self::INFINITY;
                    }
                }
                let (multiplier, power) = Self::split_value(value);
                Self { multiplier, power }
            }
        }

        #[cfg(feature = "pyo3")]
        #[pymethods]
        impl $type {
            fn __mul__(lhs: PyRef<Self>, rhs: Py<PyAny>) -> PyResult<PyObject> {
                let py = lhs.py();
                let rhs_ref = rhs.bind(py);
                let lhs_py = lhs.into_py(py);
                let lhs_ref = lhs_py.bind(py);
                let rhs_quantity = Quantity::from_py_any(rhs_ref)
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let lhs_quantity = Quantity::from_py_any(lhs_ref)
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                match lhs_quantity * rhs_quantity {
                    Ok(value) => Ok(value.to_pyobject(py)),
                    Err(_) => Err(PyValueError::new_err(
                        "Multiplication of given objects is not possible.",
                    )),
                }
            }

            fn __truediv__(lhs: PyRef<Self>, rhs: Py<PyAny>) -> PyResult<PyObject> {
                let py = lhs.py();
                let rhs_ref = rhs.bind(py);
                let lhs_py = lhs.into_py(py);
                let lhs_ref = lhs_py.bind(py);
                let rhs_quantity = Quantity::from_py_any(rhs_ref)
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let lhs_quantity = Quantity::from_py_any(lhs_ref)
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                match lhs_quantity / rhs_quantity {
                    Ok(value) => Ok(value.to_pyobject(py)),
                    Err(_) => Err(PyValueError::new_err(
                        "Division of given objects is not possible.",
                    )),
                }
            }

            fn __rmul__(&self, rhs: f64) -> PyResult<Self> {
                Ok(*self * rhs)
            }
        }

        impl fmt::Display for $type {
            fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                let base_unit = $display_unit;
                let unit_name = if base_unit.name() == "°" {
                    "°".to_string()
                } else {
                    format!(" {}", base_unit.name())
                };
                let value = self.to(base_unit);
                let rounded = if value.is_zero() {
                    value
                } else {
                    let didgits = value.log10().ceil() as i32;
                    let rounding_multiplier = 10_f64.powi(3 - didgits);
                    (value * rounding_multiplier).round() as f64 / rounding_multiplier as f64
                };

                write!(f, "{}{}", rounded, unit_name)
            }
        }

        impl Neg for $type {
            type Output = Self;

            fn neg(self) -> Self::Output {
                Self {
                    multiplier: -self.multiplier,
                    power: self.power,
                }
            }
        }

        impl PartialEq<Self> for $type
        where
            $type: PhysicsQuantity,
        {
            fn eq(&self, other: &Self) -> bool {
                self.is_close(
                    other,
                    &Self {
                        multiplier: self.multiplier,
                        power: self.power.clone() - 9,
                    },
                )
            }
        }

        impl PartialOrd for $type
        where
            $type: PhysicsQuantity,
        {
            fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                self.as_f64().partial_cmp(&other.as_f64())
            }
        }

        impl FromPrimitive for $type {
            fn from_i64(n: i64) -> Option<Self> {
                Some(Self::from_raw(n as f64))
            }

            fn from_u64(n: u64) -> Option<Self> {
                Some(Self::from_raw(n as f64))
            }

            fn from_f64(n: f64) -> Option<Self> {
                Some(Self::from_raw(n))
            }
        }

        impl Add for $type {
            type Output = Self;

            fn add(self, other: Self) -> Self {
                let common_power = self.power.max(other.power);
                let multiplier = self.multiplier * 10_f64.powi(self.power - common_power)
                    + other.multiplier * 10_f64.powi(other.power - common_power);
                let mut res = Self {
                    multiplier,
                    power: common_power,
                };
                res.optimize();
                res
            }
        }

        impl Sub for $type {
            type Output = Self;

            fn sub(self, other: Self) -> Self {
                let common_power = (self.power + other.power) / 2;
                let multiplier = self.multiplier * 10_f64.powi(self.power - common_power)
                    - other.multiplier * 10_f64.powi(other.power - common_power);

                let mut res = Self {
                    multiplier,
                    power: common_power,
                };
                res.optimize();
                res
            }
        }

        impl Div<f64> for $type {
            type Output = Self;

            fn div(self, rhs: f64) -> Self::Output {
                let (rhs_multiplier, rhs_power) = Self::split_value(rhs);
                Self {
                    multiplier: self.multiplier / rhs_multiplier,
                    power: self.power - rhs_power,
                }
            }
        }

        impl Mul<f64> for $type {
            type Output = Self;

            fn mul(self, rhs: f64) -> Self::Output {
                let (rhs_multiplier, rhs_power) = Self::split_value(rhs);
                Self {
                    multiplier: self.multiplier * rhs_multiplier,
                    power: self.power + rhs_power,
                }
            }
        }

        impl Mul<$type> for f64 {
            type Output = $type;

            fn mul(self, rhs: $type) -> Self::Output {
                rhs * self
            }
        }

        impl AddAssign for $type {
            fn add_assign(&mut self, other: Self) {
                let common_power = (self.power + other.power) / 2;
                self.multiplier = self.multiplier * 10_f64.powi(self.power - common_power)
                    + other.multiplier * 10_f64.powi(other.power - common_power);
                self.power = common_power;
                self.optimize();
            }
        }

        impl SubAssign for $type {
            fn sub_assign(&mut self, other: Self) {
                let common_power = (self.power + other.power) / 2;
                self.multiplier = self.multiplier * 10_f64.powi(self.power - common_power)
                    - other.multiplier * 10_f64.powi(other.power - common_power);
                self.power = common_power;
                self.optimize();
            }
        }

        impl MulAssign<f64> for $type {
            fn mul_assign(&mut self, rhs: f64) {
                let (rhs_multiplier, rhs_power) = Self::split_value(rhs);
                self.multiplier *= rhs_multiplier;
                self.power += rhs_power;
            }
        }

        impl DivAssign<f64> for $type {
            fn div_assign(&mut self, rhs: f64) {
                let (rhs_multiplier, rhs_power) = Self::split_value(rhs);
                self.multiplier /= rhs_multiplier;
                self.power -= rhs_power;
            }
        }

        impl Mul<Vector3<f64>> for $type {
            type Output = Vector3<$type>;

            fn mul(self, rhs: Vector3<f64>) -> Self::Output {
                Vector3::new([self * rhs[0], self * rhs[1], self * rhs[2]])
            }
        }

        impl Mul<Matrix3<f64>> for $type {
            type Output = Matrix3<$type>;

            fn mul(self, rhs: Matrix3<f64>) -> Self::Output {
                Matrix3::new([
                    [self * rhs[(0, 0)], self * rhs[(0, 1)], self * rhs[(0, 2)]],
                    [self * rhs[(1, 0)], self * rhs[(1, 1)], self * rhs[(1, 2)]],
                    [self * rhs[(2, 0)], self * rhs[(2, 1)], self * rhs[(2, 2)]],
                ])
            }
        }

        impl Zero for $type {
            fn zero() -> Self {
                Self {
                    multiplier: 0.0,
                    power: 0,
                }
            }

            fn is_zero(&self) -> bool {
                self.multiplier == 0.0
            }
        }

        impl fmt::Debug for $type {
            fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
                fmt::Display::fmt(self, f)
            }
        }

        impl QuantityArray2<$unit> for Array2<$type> {
            fn from_raw(raw: ArrayView2<f64>, unit: $unit) -> Self {
                let mut res = Array2::zeros(raw.dim());
                for i in 0..raw.dim().0 {
                    for j in 0..raw.dim().1 {
                        res[[i, j]] = <$type>::new(raw[[i, j]], unit);
                    }
                }
                res
            }

            fn to_raw(&self) -> Array2<f64> {
                let mut res = Array2::zeros(self.dim());
                for i in 0..self.dim().0 {
                    for j in 0..self.dim().1 {
                        res[[i, j]] = self[[i, j]].as_f64();
                    }
                }
                res
            }

            fn to(&self, unit: $unit) -> Array2<f64> {
                let mut res = Array2::zeros(self.dim());
                for i in 0..self.dim().0 {
                    for j in 0..self.dim().1 {
                        res[[i, j]] = self[[i, j]].to(unit);
                    }
                }
                res
            }
        }

        impl QuantityArray1<$unit> for Array1<$type> {
            fn from_raw(raw: ArrayView1<f64>, unit: $unit) -> Self {
                let mut res = Array1::zeros(raw.dim());
                for i in 0..raw.dim() {
                    res[i] = <$type>::new(raw[i], unit);
                }
                res
            }

            fn to_raw(&self) -> Array1<f64> {
                let mut res = Array1::zeros(self.dim());
                for i in 0..self.dim() {
                    res[i] = self[i].as_f64();
                }
                res
            }

            fn to(&self, unit: $unit) -> Array1<f64> {
                let mut res = Array1::zeros(self.dim());
                for i in 0..self.dim() {
                    res[i] = self[i].to(unit);
                }
                res
            }
        }

        #[cfg(feature = "pyo3")]
        #[pymethods]
        impl $type {
            #[classmethod]
            #[pyo3(name = "zero")]
            fn zero_py(_cls: &Bound<'_, PyType>) -> Self {
                Self::zero()
            }

            #[new]
            fn new_py(value: f64, unit: $unit) -> PyResult<Self> {
                Ok(Self::new(value, unit))
            }

            fn close_abs(&self, other: PyRef<Self>, threshold: Self) -> bool {
                (self.clone() - other.clone()).abs() <= threshold
            }

            fn close_rel(&self, other: PyRef<Self>, threshold: f64) -> bool {
                let mean = (self.clone() + other.clone()) / 2.;
                (self.clone() - other.clone()).abs() <= mean * threshold
            }

            fn __richcmp__(&self, other: PyRef<Self>, op: CompareOp) -> Py<PyAny> {
                let py = other.py();
                match op {
                    CompareOp::Lt => (self.clone() < other.clone()).into_py(py),
                    CompareOp::Le => (self.clone() <= other.clone()).into_py(py),
                    CompareOp::Eq => (self.clone() == other.clone()).into_py(py),
                    CompareOp::Ne => (self.clone() != other.clone()).into_py(py),
                    CompareOp::Gt => (self.clone() > other.clone()).into_py(py),
                    CompareOp::Ge => (self.clone() >= other.clone()).into_py(py),
                }
            }

            fn __repr__(&self) -> PyResult<String> {
                Ok(format!("{:?}", self))
            }

            fn __str__(&self) -> PyResult<String> {
                Ok(format!("{:?}", self))
            }

            fn __add__(lhs: PyRef<Self>, rhs: PyRef<Self>) -> PyResult<Self> {
                Ok(lhs.clone() + rhs.clone())
            }

            fn __sub__(lhs: PyRef<Self>, rhs: PyRef<Self>) -> PyResult<Self> {
                Ok(lhs.clone() - rhs.clone())
            }

            fn __abs__(&self) -> Self {
                self.abs()
            }

            #[allow(clippy::wrong_self_convention)]
            #[pyo3(name = "to")]
            fn to_py(&self, unit: $unit) -> f64 {
                self.to(unit)
            }
        }
    };
}

#[macro_export]
macro_rules! impl_const {
    ($type:ident, $name:ident, $multiplier:expr, $power:expr) => {
        #[cfg(feature = "pyo3")]
        #[pymethods]
        impl $type {
            #[staticmethod]
            pub fn $name() -> Self {
                Self {
                    multiplier: $multiplier,
                    power: $power,
                }
            }
        }
        #[cfg(not(feature = "pyo3"))]
        impl $type {
            pub fn $name() -> Self {
                Self {
                    multiplier: $multiplier,
                    power: $power,
                }
            }
        }
    };
}

#[macro_export]
macro_rules! impl_div_with_self_to_f64 {
    ($lhs:ty) => {
        impl Div<$lhs> for $lhs {
            type Output = f64;

            fn div(self, rhs: Self) -> Self::Output {
                (self.multiplier / rhs.multiplier) * 10_f64.powi(self.power - rhs.power)
            }
        }
    };
}

#[macro_export]
macro_rules! impl_mul {
    ($lhs:ty, $rhs:ty, $result:ty) => {
        impl std::ops::Mul<$rhs> for $lhs {
            type Output = $result;

            fn mul(self, rhs: $rhs) -> Self::Output {
                <$result>::from_exponential(
                    self.multiplier * rhs.multiplier,
                    self.power + rhs.power,
                )
            }
        }

        impl std::ops::Mul<$lhs> for $rhs {
            type Output = $result;

            fn mul(self, rhs: $lhs) -> Self::Output {
                <$result>::from_exponential(
                    self.multiplier * rhs.multiplier,
                    self.power + rhs.power,
                )
            }
        }

        impl MulArray1<$rhs> for Array1<$lhs> {
            type Output = Array1<$result>;

            fn mul_array1(self, rhs: Array1<$rhs>) -> Array1<$result> {
                self.into_iter()
                    .zip(rhs.into_iter())
                    .map(|(force, distance)| force * distance)
                    .collect()
            }
        }

        impl MulArray2<$rhs> for Array2<$lhs> {
            type Output = Array2<$result>;

            fn mul_array2(self, rhs: Array2<$rhs>) -> Result<Array2<$result>, String> {
                let mut results = Vec::new();

                for (lhs_row, rhs_row) in self.outer_iter().zip(rhs.outer_iter()) {
                    let result_row: Array1<$result> = lhs_row
                        .iter()
                        .zip(rhs_row.iter())
                        .map(|(&lhs, &rhs)| lhs * rhs)
                        .collect();
                    results.push(result_row);
                }

                let nrows = results.len();
                let ncols = if nrows > 0 { results[0].len() } else { 0 };
                let data: Vec<$result> = results
                    .into_iter()
                    .flat_map(|r| {
                        let (raw_vec, _) = r.into_raw_vec_and_offset();
                        raw_vec
                    })
                    .collect();

                Array2::from_shape_vec((nrows, ncols), data)
                    .map_err(|_| "Shape mismatch".to_string())
            }
        }

        impl MulArray1<$lhs> for Array1<$rhs> {
            type Output = Array1<$result>;

            fn mul_array1(self, rhs: Array1<$lhs>) -> Array1<$result> {
                self.into_iter()
                    .zip(rhs.into_iter())
                    .map(|(force, distance)| force * distance)
                    .collect()
            }
        }

        impl MulArray2<$lhs> for Array2<$rhs> {
            type Output = Array2<$result>;

            fn mul_array2(self, rhs: Array2<$lhs>) -> Result<Array2<$result>, String> {
                let mut results = Vec::new();

                for (force_row, distance_row) in self.outer_iter().zip(rhs.outer_iter()) {
                    let result_row: Array1<$result> = force_row
                        .iter()
                        .zip(distance_row.iter())
                        .map(|(&force, &distance)| force * distance)
                        .collect();
                    results.push(result_row);
                }

                let nrows = results.len();
                let ncols = if nrows > 0 { results[0].len() } else { 0 };
                let data: Vec<$result> = results
                    .into_iter()
                    .flat_map(|r| {
                        let (raw_vec, _) = r.into_raw_vec_and_offset();
                        raw_vec
                    })
                    .collect();

                Array2::from_shape_vec((nrows, ncols), data)
                    .map_err(|_| "Shape mismatch".to_string())
            }
        }
    };
}

#[macro_export]
macro_rules! impl_mul_with_self {
    ($lhs:ty,$result:ty) => {
        impl std::ops::Mul<$lhs> for $lhs {
            type Output = $result;

            fn mul(self, rhs: $lhs) -> Self::Output {
                <$result>::from_exponential(
                    self.multiplier * rhs.multiplier,
                    self.power + rhs.power,
                )
            }
        }

        impl MulArray1<$lhs> for Array1<$lhs> {
            type Output = Array1<$result>;

            fn mul_array1(self, rhs: Array1<$lhs>) -> Array1<$result> {
                self.into_iter()
                    .zip(rhs.into_iter())
                    .map(|(force, distance)| force * distance)
                    .collect()
            }
        }

        impl MulArray2<$lhs> for Array2<$lhs> {
            type Output = Array2<$result>;

            fn mul_array2(self, rhs: Array2<$lhs>) -> Result<Array2<$result>, String> {
                let mut results = Vec::new();

                for (force_row, distance_row) in self.outer_iter().zip(rhs.outer_iter()) {
                    let result_row: Array1<$result> = force_row
                        .iter()
                        .zip(distance_row.iter())
                        .map(|(&force, &distance)| force * distance)
                        .collect();
                    results.push(result_row);
                }

                let nrows = results.len();
                let ncols = if nrows > 0 { results[0].len() } else { 0 };
                let data: Vec<$result> = results
                    .into_iter()
                    .flat_map(|r| {
                        let (raw_vec, _) = r.into_raw_vec_and_offset();
                        raw_vec
                    })
                    .collect();

                Array2::from_shape_vec((nrows, ncols), data)
                    .map_err(|_| "Shape mismatch".to_string())
            }
        }
    };
}

#[macro_export]
macro_rules! impl_div {
    ($lhs:ty, $rhs:ty, $result:ty) => {
        impl std::ops::Div<$rhs> for $lhs {
            type Output = $result;

            fn div(self, rhs: $rhs) -> Self::Output {
                <$result>::from_exponential(
                    self.multiplier / rhs.multiplier,
                    self.power - rhs.power,
                )
            }
        }

        impl DivArray1<$rhs> for Array1<$lhs> {
            type Output = Array1<$result>;

            fn div_array1(self, rhs: Array1<$rhs>) -> Array1<$result> {
                self.into_iter()
                    .zip(rhs.into_iter())
                    .map(|(force, distance)| force / distance)
                    .collect()
            }
        }

        impl DivArray2<$rhs> for Array2<$lhs> {
            type Output = Array2<$result>;

            fn div_array2(self, rhs: Array2<$rhs>) -> Result<Array2<$result>, String> {
                let mut results = Vec::new();

                for (force_row, distance_row) in self.outer_iter().zip(rhs.outer_iter()) {
                    let result_row: Array1<$result> = force_row
                        .iter()
                        .zip(distance_row.iter())
                        .map(|(&force, &distance)| force / distance)
                        .collect();
                    results.push(result_row);
                }

                let nrows = results.len();
                let ncols = if nrows > 0 { results[0].len() } else { 0 };
                let data: Vec<$result> = results
                    .into_iter()
                    .flat_map(|r| {
                        let (raw_vec, _) = r.into_raw_vec_and_offset();
                        raw_vec
                    })
                    .collect();

                Array2::from_shape_vec((nrows, ncols), data)
                    .map_err(|_| "Shape mismatch".to_string())
            }
        }
    };
}

#[macro_export]
macro_rules! impl_sqrt {
    ($lhs:ty, $res:ty) => {
        impl Sqrt<$res> for $lhs {
            fn sqrt(self) -> $res {
                if self.power % 2 == 0 {
                    <$res>::from_exponential(self.multiplier.sqrt(), self.power / 2)
                } else {
                    <$res>::from_exponential(
                        self.multiplier.sqrt() * 10_f64.sqrt(),
                        (self.power - 1) / 2,
                    )
                }
            }
        }
        #[cfg(feature = "pyo3")]
        #[pymethods]
        impl $lhs {
            #[pyo3(name = "sqrt")]
            fn sqrt_py(&self) -> $res {
                self.sqrt()
            }
        }
    };
}

#[macro_export]
macro_rules! impl_mul_relation_with_self {
    ($lhs:ty, $res:ty) => {
        impl_mul_with_self!($lhs, $res);
        impl_sqrt!($res, $lhs);
        impl_div!($res, $lhs, $lhs);
    };
}

#[macro_export]
macro_rules! impl_mul_relation_with_other {
    ($lhs:ty, $rhs:ty, $res:ty) => {
        impl_mul!($lhs, $rhs, $res);
        impl_div!($res, $lhs, $rhs);
        impl_div!($res, $rhs, $lhs);
    };
}

pub mod macros {
    pub use crate::impl_const;
    pub use crate::impl_div;
    pub use crate::impl_div_with_self_to_f64;
    pub use crate::impl_mul;
    pub use crate::impl_mul_relation_with_other;
    pub use crate::impl_mul_relation_with_self;
    pub use crate::impl_mul_with_self;
    pub use crate::impl_quantity;
    pub use crate::impl_sqrt;
}
