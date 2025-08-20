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
pub enum AreaUnit {
    kmsq,
    msq,
    dmsq,
    cmsq,
    mmsq,
    mumsq,
    nmsq,
    sqmi,
    sqyd,
    sqft,
    sqin,
}

impl PhysicsUnit for AreaUnit {
    fn name(&self) -> &str {
        match &self {
            AreaUnit::kmsq => "km²",
            AreaUnit::msq => "m²",
            AreaUnit::dmsq => "dm²",
            AreaUnit::cmsq => "cm²",
            AreaUnit::mmsq => "mm²",
            AreaUnit::mumsq => "μm²",
            AreaUnit::nmsq => "nm²",
            AreaUnit::sqmi => "mi²",
            AreaUnit::sqyd => "yd²",
            AreaUnit::sqft => "ft²",
            AreaUnit::sqin => "in²",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            AreaUnit::kmsq => (1., 6),
            AreaUnit::msq => (1., 0),
            AreaUnit::dmsq => (1., -2),
            AreaUnit::cmsq => (1., -4),
            AreaUnit::mmsq => (1., -6),
            AreaUnit::mumsq => (1., -12),
            AreaUnit::nmsq => (1., -18),
            AreaUnit::sqmi => (2.59, 6),
            AreaUnit::sqyd => (0.8361, 0),
            AreaUnit::sqft => (9.2903, -2),
            AreaUnit::sqin => (6.4516, -4),
        }
    }
}

impl_quantity!(Area, AreaUnit, AreaUnit::mmsq);
impl_div_with_self_to_f64!(Area);
