use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::PhysicsUnit;
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
pub enum StiffnessUnit {
    N_mm,
    kN_mm,
    N_m,
    kN_m,
}

impl PhysicsUnit for StiffnessUnit {
    fn name(&self) -> &str {
        match &self {
            StiffnessUnit::N_mm => "N/mm",
            StiffnessUnit::kN_mm => "kN/mm",
            StiffnessUnit::N_m => "N/m",
            StiffnessUnit::kN_m => "kN/m",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            StiffnessUnit::N_mm => (1., 3),
            StiffnessUnit::kN_mm => (1., 6),
            StiffnessUnit::N_m => (1., 0),
            StiffnessUnit::kN_m => (1., 3),
        }
    }
}

impl_quantity!(Stiffness, StiffnessUnit, StiffnessUnit::N_mm);
impl_div_with_self_to_f64!(Stiffness);
