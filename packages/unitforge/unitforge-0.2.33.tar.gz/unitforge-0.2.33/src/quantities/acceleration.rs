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
pub enum AccelerationUnit {
    m_ssq,
    cm_ssq,
    mm_ssq,
}

impl PhysicsUnit for AccelerationUnit {
    fn name(&self) -> &str {
        match &self {
            AccelerationUnit::m_ssq => "m/s²",
            AccelerationUnit::cm_ssq => "cm/s²",
            AccelerationUnit::mm_ssq => "mm/s²",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            AccelerationUnit::m_ssq => (1., 0),
            AccelerationUnit::cm_ssq => (1., 2),
            AccelerationUnit::mm_ssq => (1., 3),
        }
    }
}

impl_const!(Acceleration, g, 9.81, 0);
impl_const!(Acceleration, g_moon, 1.62, 0);
impl_const!(Acceleration, g_mars, 3.73, 0);

impl_quantity!(Acceleration, AccelerationUnit, AccelerationUnit::m_ssq);
impl_div_with_self_to_f64!(Acceleration);
