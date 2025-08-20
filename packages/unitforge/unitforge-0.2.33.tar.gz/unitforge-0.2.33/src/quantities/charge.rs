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
pub enum ChargeUnit {
    C,
}

impl PhysicsUnit for ChargeUnit {
    fn name(&self) -> &str {
        match &self {
            ChargeUnit::C => "C",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ChargeUnit::C => (1., 0),
        }
    }
}

impl_const!(Charge, e, 1.602176634, -19);

impl_quantity!(Charge, ChargeUnit, ChargeUnit::C);
impl_div_with_self_to_f64!(Charge);
