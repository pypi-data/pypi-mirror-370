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
pub enum DistanceUnit {
    km,
    m,
    dm,
    cm,
    mm,
    um,
    nm,
    mi,
    yd,
    ft,
    inch,
    planck,
    fm,
    an,
    AU,
    ly,
    pc,
    kpc,
    Mpc,
    Gpc,
    solar_radius,
    earth_radius,
    lunar_radius,
    jupiter_radius,
}

impl PhysicsUnit for DistanceUnit {
    fn name(&self) -> &str {
        match &self {
            DistanceUnit::km => "km",
            DistanceUnit::m => "m",
            DistanceUnit::dm => "dm",
            DistanceUnit::cm => "cm",
            DistanceUnit::mm => "mm",
            DistanceUnit::um => "μm",
            DistanceUnit::nm => "nm",
            DistanceUnit::mi => "mi",
            DistanceUnit::yd => "yd",
            DistanceUnit::ft => "ft",
            DistanceUnit::inch => "in",
            DistanceUnit::planck => "Planck Distance",
            DistanceUnit::fm => "fm",
            DistanceUnit::an => "Å",
            DistanceUnit::AU => "AU",
            DistanceUnit::ly => "ly",
            DistanceUnit::pc => "py",
            DistanceUnit::kpc => "kpc",
            DistanceUnit::Mpc => "MPc",
            DistanceUnit::Gpc => "GPc",
            DistanceUnit::solar_radius => "M☉",
            DistanceUnit::earth_radius => "M⊕",
            DistanceUnit::lunar_radius => "M☽",
            DistanceUnit::jupiter_radius => "M♃",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            DistanceUnit::km => (1.0, 3),
            DistanceUnit::m => (1.0, 0),
            DistanceUnit::dm => (1.0, -1),
            DistanceUnit::cm => (1.0, -2),
            DistanceUnit::mm => (1.0, -3),
            DistanceUnit::um => (1.0, -6),
            DistanceUnit::nm => (1.0, -9),
            DistanceUnit::mi => (1.609344, 3),
            DistanceUnit::yd => (9.144, -1),
            DistanceUnit::ft => (3.048, -1),
            DistanceUnit::inch => (2.54, -2),
            DistanceUnit::planck => (1.616255, -35),
            DistanceUnit::fm => (1., -15),
            DistanceUnit::an => (1., -10),
            DistanceUnit::AU => (1.49597870700, 11),
            DistanceUnit::ly => (Time::new(1., TimeUnit::year) * Velocity::c()).get_tuple(),
            DistanceUnit::pc => (3.085677581, 16),
            DistanceUnit::kpc => (3.085677581, 16 + 3),
            DistanceUnit::Mpc => (3.085677581, 16 + 6),
            DistanceUnit::Gpc => (3.085677581, 16 + 9),
            DistanceUnit::solar_radius => (6.957, 8),
            DistanceUnit::earth_radius => (6.3781, 6),
            DistanceUnit::lunar_radius => (1.738, 6),
            DistanceUnit::jupiter_radius => (7.1492, 7),
        }
    }
}

impl_const!(Distance, a_0, 5.29177210544, -11);
impl_const!(Distance, r_e, 2.8179403227, -15);

impl_quantity!(Distance, DistanceUnit, DistanceUnit::mm);
impl_div_with_self_to_f64!(Distance);

impl_mul!(Distance, Strain, Distance);
