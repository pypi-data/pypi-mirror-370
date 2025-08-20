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
pub enum VelocityUnit {
    km_s,
    m_s,
    cm_s,
    mm_s,
    km_h,
}

impl PhysicsUnit for VelocityUnit {
    fn name(&self) -> &str {
        match &self {
            VelocityUnit::km_s => "km/s",
            VelocityUnit::m_s => "m/s",
            VelocityUnit::cm_s => "cm/s",
            VelocityUnit::mm_s => "mm/s",
            VelocityUnit::km_h => "km/h",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            VelocityUnit::km_s => (1., 3),
            VelocityUnit::m_s => (1., 0),
            VelocityUnit::cm_s => (1., 2),
            VelocityUnit::mm_s => (1., 3),
            VelocityUnit::km_h => (1. / 3.6, 0),
        }
    }
}

impl_const!(Velocity, c, 2.99792458, 8);

impl_quantity!(Velocity, VelocityUnit, VelocityUnit::m_s);
impl_div_with_self_to_f64!(Velocity);
