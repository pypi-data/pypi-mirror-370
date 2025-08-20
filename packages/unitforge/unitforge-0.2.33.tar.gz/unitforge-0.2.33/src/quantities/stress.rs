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
pub enum StressUnit {
    Pa,
    kPa,
    bar,
    MPa,
    GPa,
    psi,
}

impl PhysicsUnit for StressUnit {
    fn name(&self) -> &str {
        match &self {
            StressUnit::Pa => "Pa",
            StressUnit::kPa => "kPa",
            StressUnit::bar => "bar",
            StressUnit::MPa => "MPa",
            StressUnit::GPa => "GPa",
            StressUnit::psi => "psi",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            StressUnit::Pa => (1., 0),
            StressUnit::kPa => (1., 3),
            StressUnit::MPa => (1., 6),
            StressUnit::bar => (1., 5),
            StressUnit::GPa => (1., 9),
            StressUnit::psi => (6.895, 3),
        }
    }
}

impl_quantity!(Stress, StressUnit, StressUnit::MPa);
impl_div_with_self_to_f64!(Stress);
impl_div!(Stress, Strain, Stress);
impl_mul!(Stress, Strain, Stress);
