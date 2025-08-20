use std::fmt::Display;
use std::cmp::Ordering;
use std::fmt;
use std::fmt::Formatter;
use std::ops::{Add, Sub, Mul, Div};
#[cfg(feature = "pyo3")]
use pyo3::{Bound, PyAny, prelude::*};

#[derive(Debug)]
pub enum QuantityOperationError {
    AddError,
    SubError,
    MulError,
    DivError,
    SqrtError,
    ComparisonError,
}

impl fmt::Display for QuantityOperationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            QuantityOperationError::AddError => write!(f, "Addition operation failed"),
            QuantityOperationError::SubError => write!(f, "Subtraction operation failed"),
            QuantityOperationError::MulError => write!(f, "Multiplication operation failed"),
            QuantityOperationError::DivError => write!(f, "Division operation failed"),
            QuantityOperationError::SqrtError => write!(f, "Sqrt operation failed"),
            QuantityOperationError::ComparisonError => write!(f, "Comparison operation failed"),
        }
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Quantity {
    //Is used for runtime checked operations with quantities
    FloatQuantity(f64),
    // __QUANTITY_VARIANTS__
}

impl Quantity {
    pub fn to(&self, unit: Unit) -> Result<f64, String> {
        match (self, unit) {
            (Quantity::FloatQuantity(value), Unit::NoUnit) => Ok(*value),
            // __QUANTITY_TO_VARIANTS__
            _ => Err("Cannot use given pair of quantity and unit.".to_string())
        }
    }

    pub fn abs(&self) -> Quantity {
        match self {
            Quantity::FloatQuantity(value) => Quantity::FloatQuantity(value.abs()),
            // __QUANTITY_ABS_VARIANTS__
        }
    }

    pub fn is_nan(&self) -> bool {
        match self {
            Quantity::FloatQuantity(value) => value.is_nan(),
            // __QUANTITY_NAN_VARIANTS__
        }
    }
}



#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Unit {
    //Is used for runtime checked operations with quantities
    NoUnit,
    // __UNIT_VARIANTS__
}

impl Display for Unit {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        write!(f, "{}", self.get_name())
    }
}

impl Unit {
    pub fn to_quantity(&self, value: f64) -> Quantity {
        match self {
            Unit::NoUnit => Quantity::FloatQuantity(value),
            // __TO_QUANTITY_VARIANTS__
        }
    }

    pub fn get_name(&self) -> &str {
        match self {
            Unit::NoUnit => "No Unit",
            // __TO_UNIT_NAME_VARIANTS__
        }
    }
}

impl Mul for Quantity {
    type Output = Result<Quantity, QuantityOperationError>;
    fn mul(self, other: Quantity) -> Result<Quantity, QuantityOperationError> {
        fn try_multiply(lhs: &Quantity, rhs: &Quantity) -> Result<Quantity, QuantityOperationError> {
            use Quantity::*;
            match (lhs, rhs) {
                (FloatQuantity(v_lhs), FloatQuantity(v_rhs)) => Ok(FloatQuantity(v_lhs * v_rhs)),
                // __MUL_MATCHES__
                _ => Err(QuantityOperationError::MulError)
            }
        }
        match try_multiply(&self, &other) {
            Ok(result) => Ok(result),
            Err(_) => try_multiply(&other, &self)
        }
    }
}

impl Div for Quantity {
    type Output = Result<Quantity, QuantityOperationError>;
    fn div(self, other: Quantity) -> Result<Quantity, QuantityOperationError> {
        use Quantity::*;
        match (self, other) {
            (FloatQuantity(v_lhs), FloatQuantity(v_rhs)) => Ok(FloatQuantity(v_lhs / v_rhs)),
            // __DIV_MATCHES__
            _ => Err(QuantityOperationError::DivError)
        }
    }
}

impl Add for Quantity {
    type Output = Result<Quantity, QuantityOperationError>;
    fn add(self, other: Quantity) -> Result<Quantity, QuantityOperationError> {
        use Quantity::*;
        match (self, other) {
            (Quantity::FloatQuantity(v_lhs), Quantity::FloatQuantity(v_rhs)) => Ok(Quantity::FloatQuantity(v_lhs + v_rhs)),
            // __ADD_QUANTITY_MATCHES__
            _ => Err(QuantityOperationError::AddError)
        }
    }
}

impl Sub for Quantity {
    type Output = Result<Quantity, QuantityOperationError>;
    fn sub(self, other: Quantity) -> Result<Self, QuantityOperationError> {
        use Quantity::*;
        match (self, other) {
            (Quantity::FloatQuantity(v_lhs), Quantity::FloatQuantity(v_rhs)) => Ok(Quantity::FloatQuantity(v_lhs - v_rhs)),
            // __SUB_QUANTITY_MATCHES__
            _ => Err(QuantityOperationError::SubError)
        }
    }
}

impl Quantity {
    pub fn extract_float(&self) -> Result<f64, String> {
        match self {
            Quantity::FloatQuantity(v) => Ok(*v),
            _ => Err("Cannot extract float from Quantity enum".into()),
        }
    }

    // __BASE_QUANTITY_MATCHES__
    pub fn sqrt(&self) -> Result<Self, QuantityOperationError> {
        match self {
            Quantity::FloatQuantity(v) => Ok(Self::FloatQuantity(v.sqrt())),
            // __QUANTITY_SQRTS__
            _=> Err(QuantityOperationError::SqrtError)
        }
    }
}

impl PartialOrd for Quantity {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        use Quantity::*;
        match (self, other) {
            (FloatQuantity(lhs), FloatQuantity(rhs)) => lhs.partial_cmp(rhs),
            // __QUANTITY_COMPARISONS__
            _ => panic!("Cannot compare non matching quantities!")
        }
    }
}

#[cfg(feature = "pyo3")]
fn extract_f64(v: &Bound<PyAny>) -> Option<f64> {
    if let Ok(inner) = v.extract::<f64>() {
        Some(inner)
    } else if let Ok(inner) = v.extract::<f32>() {
        Some(inner as f64)
    } else if let Ok(inner) = v.extract::<i32>() {
        Some(inner as f64)
    } else if let Ok(inner) = v.extract::<i64>() {
        Some(inner as f64)
    } else {
        None
    }
}

#[cfg(feature = "pyo3")]
impl Quantity {
    pub fn from_py_any(v: &Bound<PyAny>) -> Result<Self, String> {
        if let Some(inner) = extract_f64(v) {
            Ok(Quantity::FloatQuantity(inner))
        }
        // __EXTRACT_QUANTITY_MATCHES__
        else {
            Err("Cannot interpret given value as Quantity".to_string())
        }
    }

    pub fn to_pyobject(self, py: Python) -> PyObject {
        match self {
            Quantity::FloatQuantity(v) => v.into_py(py),
            // __TO_PYOBJECT_MATCHES__
        }
    }
}

impl Display for Quantity {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        match self {
            Quantity::FloatQuantity(v) => write!(f, "{v}"),
            // __QUANTITY_FMT_MATCHES__
        }
    }
}

#[cfg(feature = "pyo3")]
impl Unit {

    pub fn from_py_any(v: &Bound<PyAny>) -> Result<Self, String> {
        // __EXTRACT_UNIT_MATCHES__
        else {
            Err("Cannot interpret given value as Quantity".to_string())
        }
    }
}