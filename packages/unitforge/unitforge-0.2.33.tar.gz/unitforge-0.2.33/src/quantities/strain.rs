use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::{Distance, PhysicsUnit, Stress};
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
pub enum StrainUnit {
    m_m,
    dm_m,
    cm_m,
    mm_m,
    um_m,
}

impl PhysicsUnit for StrainUnit {
    fn name(&self) -> &str {
        match &self {
            StrainUnit::m_m => "m/m",
            StrainUnit::dm_m => "dm/m",
            StrainUnit::cm_m => "cm/m",
            StrainUnit::mm_m => "mm/m",
            StrainUnit::um_m => "μm/m",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            StrainUnit::m_m => (1., 0),
            StrainUnit::dm_m => (1., -1),
            StrainUnit::cm_m => (1., -2),
            StrainUnit::mm_m => (1., -3),
            StrainUnit::um_m => (1., -6),
        }
    }
}

impl Strain {
    pub fn from_distances(numerator: Distance, denominator: Distance) -> Self {
        Self::from_raw(numerator / denominator)
    }
    pub fn from_stresses(numerator: Stress, denominator: Stress) -> Self {
        Self::from_raw(numerator / denominator)
    }
}

impl_quantity!(Strain, StrainUnit, StrainUnit::m_m);
impl_div_with_self_to_f64!(Strain);
impl_div!(Strain, Distance, Distance);
