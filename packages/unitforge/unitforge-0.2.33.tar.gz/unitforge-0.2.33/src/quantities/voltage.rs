use crate::impl_macros::macros::*;
use crate::prelude::*;
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
pub enum VoltageUnit {
    V,
    kV,
    MV,
    GV,
    TV,
}

impl PhysicsUnit for VoltageUnit {
    fn name(&self) -> &str {
        match &self {
            VoltageUnit::V => "V",
            VoltageUnit::kV => "kV",
            VoltageUnit::MV => "MV",
            VoltageUnit::GV => "GV",
            VoltageUnit::TV => "TV",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            VoltageUnit::V => (1., 0),
            VoltageUnit::kV => (1., 3),
            VoltageUnit::MV => (1., 6),
            VoltageUnit::GV => (1., 9),
            VoltageUnit::TV => (1., 12),
        }
    }
}

impl_quantity!(Voltage, VoltageUnit, VoltageUnit::V);
impl_div_with_self_to_f64!(Voltage);
