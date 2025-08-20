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
pub enum TimeUnit {
    ns,
    us,
    ms,
    s,
    min,
    h,
    day,
    week,
    month,
    year,
}

impl PhysicsUnit for TimeUnit {
    fn name(&self) -> &str {
        match &self {
            TimeUnit::ns => "ns",
            TimeUnit::us => "μm",
            TimeUnit::ms => "ms",
            TimeUnit::s => "s",
            TimeUnit::min => "min",
            TimeUnit::h => "h",
            TimeUnit::day => "day",
            TimeUnit::week => "week",
            TimeUnit::month => "month",
            TimeUnit::year => "year",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            TimeUnit::ns => (1., -9),
            TimeUnit::us => (1., -6),
            TimeUnit::ms => (1., -3),
            TimeUnit::s => (1., 0),
            TimeUnit::min => (6., 1),
            TimeUnit::h => (3.6, 2),
            TimeUnit::day => (8.6400, 4),
            TimeUnit::week => (6.04800, 5),
            TimeUnit::month => (2.62800288, 6),
            TimeUnit::year => (3.1556952, 7),
        }
    }
}

impl_quantity!(Time, TimeUnit, TimeUnit::s);
impl_div_with_self_to_f64!(Time);
