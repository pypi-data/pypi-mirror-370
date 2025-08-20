use crate::impl_macros::macros::*;
use crate::prelude::*;
use crate::PhysicsUnit;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::{FloatConst, FromPrimitive};
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::f64::consts::PI;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum AngleUnit {
    rad,
    deg,
}

impl PhysicsUnit for AngleUnit {
    fn name(&self) -> &str {
        match &self {
            AngleUnit::rad => "rad",
            AngleUnit::deg => "°",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            AngleUnit::rad => (1., 0),
            AngleUnit::deg => (PI / 180., 0),
        }
    }
}

impl_const!(Angle, pi, f64::PI(), 0);
impl_const!(Angle, perpendicular, f64::PI() / 2., 0);

impl_quantity!(Angle, AngleUnit, AngleUnit::deg);
impl_div_with_self_to_f64!(Angle);

impl Angle {
    pub fn sin(&self) -> f64 {
        self.as_f64().sin()
    }

    pub fn cos(&self) -> f64 {
        self.as_f64().cos()
    }

    pub fn tan(&self) -> f64 {
        self.as_f64().tan()
    }

    pub fn arc_sin(value: f64) -> Self {
        Self {
            multiplier: value.asin(),
            power: 0,
        }
    }

    pub fn arc_cos(value: f64) -> Self {
        Self {
            multiplier: value.acos(),
            power: 0,
        }
    }

    pub fn arc_tan(value: f64) -> Self {
        Self {
            multiplier: value.atan(),
            power: 0,
        }
    }

    pub fn arc_tan_2(x: f64, y: f64) -> Self {
        Self {
            multiplier: f64::atan2(x, y),
            power: 0,
        }
    }
}
