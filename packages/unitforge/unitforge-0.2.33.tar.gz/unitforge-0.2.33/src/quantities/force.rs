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
pub enum ForceUnit {
    GN,
    MN,
    kN,
    N,
    dN,
    cN,
    mN,
    muN,
    nN,
    lbf,
    kgf,
}

impl PhysicsUnit for ForceUnit {
    fn name(&self) -> &str {
        match &self {
            ForceUnit::GN => "GN",
            ForceUnit::MN => "MN",
            ForceUnit::kN => "kN",
            ForceUnit::N => "N",
            ForceUnit::dN => "dN",
            ForceUnit::cN => "cN",
            ForceUnit::mN => "mN",
            ForceUnit::muN => "μm",
            ForceUnit::nN => "nN",
            ForceUnit::lbf => "lbf",
            ForceUnit::kgf => "kgf",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ForceUnit::GN => (1., 9),
            ForceUnit::MN => (1., 6),
            ForceUnit::kN => (1., 3),
            ForceUnit::N => (1., 0),
            ForceUnit::dN => (1., -1),
            ForceUnit::cN => (1., -2),
            ForceUnit::mN => (1., -3),
            ForceUnit::muN => (1., -6),
            ForceUnit::nN => (1., -9),
            ForceUnit::lbf => (4.44822, 0),
            ForceUnit::kgf => (9.80665, 0),
        }
    }
}

impl_quantity!(Force, ForceUnit, ForceUnit::N);
impl_div_with_self_to_f64!(Force);
