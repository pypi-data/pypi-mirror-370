use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::quantities::*;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::FromPrimitive;
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum InverseDistanceUnit {
    _km,
    _m,
    _dm,
    _cm,
    _mm,
    _um,
    _nm,
    _mi,
    _yd,
    _ft,
    _inch,
}

impl PhysicsUnit for InverseDistanceUnit {
    fn name(&self) -> &str {
        match &self {
            InverseDistanceUnit::_km => "1/km",
            InverseDistanceUnit::_m => "1/m",
            InverseDistanceUnit::_dm => "1/dm",
            InverseDistanceUnit::_cm => "1/cm",
            InverseDistanceUnit::_mm => "1/mm",
            InverseDistanceUnit::_um => "1/μm",
            InverseDistanceUnit::_nm => "1/nm",
            InverseDistanceUnit::_mi => "1/mi",
            InverseDistanceUnit::_yd => "1/yd",
            InverseDistanceUnit::_ft => "1/ft",
            InverseDistanceUnit::_inch => "1/in",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            InverseDistanceUnit::_km => (1., -3),
            InverseDistanceUnit::_m => (1., 0),
            InverseDistanceUnit::_dm => (1., 1),
            InverseDistanceUnit::_cm => (1., 2),
            InverseDistanceUnit::_mm => (1., 3),
            InverseDistanceUnit::_um => (1., 6),
            InverseDistanceUnit::_nm => (1., 9),
            InverseDistanceUnit::_mi => (0.62137, -3),
            InverseDistanceUnit::_yd => (0.10936, 1),
            InverseDistanceUnit::_ft => (0.32808, 1),
            InverseDistanceUnit::_inch => (0.393700787, 2),
        }
    }
}

impl_quantity!(
    InverseDistance,
    InverseDistanceUnit,
    InverseDistanceUnit::_mm
);
impl_div_with_self_to_f64!(InverseDistance);

impl_mul!(InverseDistance, Distance, f64);
