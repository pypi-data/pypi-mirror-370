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
pub enum MassUnit {
    mg,
    g,
    kg,
    t,
    Mg,
    kt,
    Gg,
    oz,  // Ounce
    lb,  // Pound
    st,  // Stone
    cwt, // Hundredweight (US)
    planck,
    u,
    keV_c2,
    eV_c2,
    MeV_c2,
    GeV_c2,
    TeV_c2,
    solar_mass,
    earth_mass,
    lunar_mass,
    jupiter_mass,
}

impl PhysicsUnit for MassUnit {
    fn name(&self) -> &str {
        match &self {
            MassUnit::mg => "mg",
            MassUnit::g => "g",
            MassUnit::kg => "kg",
            MassUnit::t => "t",
            MassUnit::kt => "kt",
            MassUnit::Mg => "Mg",
            MassUnit::Gg => "Gg",
            MassUnit::oz => "oz",
            MassUnit::lb => "lb",
            MassUnit::st => "st",
            MassUnit::cwt => "cwt",
            MassUnit::planck => "Planck Mass",
            MassUnit::u => "Atomic mass unit",
            MassUnit::eV_c2 => "eV/c²",
            MassUnit::keV_c2 => "keV/c²",
            MassUnit::MeV_c2 => "MeV/c²",
            MassUnit::GeV_c2 => "MeV/c²",
            MassUnit::TeV_c2 => "TeV/c²",
            MassUnit::solar_mass => "M☉",
            MassUnit::earth_mass => "M⊕",
            MassUnit::lunar_mass => "M☽",
            MassUnit::jupiter_mass => "M♃",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            MassUnit::mg => (1., -6),
            MassUnit::g => (1., -3),
            MassUnit::kg => (1., 0),
            MassUnit::t => (1., 3),
            MassUnit::kt => (1., 6),
            MassUnit::Mg => (1., 3),
            MassUnit::Gg => (1., 6),
            MassUnit::oz => (2.83495, -2),
            MassUnit::lb => (4.5359, -1),
            MassUnit::st => (6.35029, 0),
            MassUnit::cwt => (5.08023, 1),
            MassUnit::planck => (2.17643424, -8),
            MassUnit::u => (1.6605390689252, -27),
            MassUnit::eV_c2 => (ForceDistance::new(1., ForceDistanceUnit::eV)
                / power!(Velocity::c(), 2))
            .get_tuple(),
            MassUnit::keV_c2 => (ForceDistance::new(1., ForceDistanceUnit::keV)
                / power!(Velocity::c(), 2))
            .get_tuple(),
            MassUnit::MeV_c2 => (ForceDistance::new(1., ForceDistanceUnit::MeV)
                / power!(Velocity::c(), 2))
            .get_tuple(),
            MassUnit::GeV_c2 => (ForceDistance::new(1., ForceDistanceUnit::GeV)
                / power!(Velocity::c(), 2))
            .get_tuple(),
            MassUnit::TeV_c2 => (ForceDistance::new(1., ForceDistanceUnit::TeV)
                / power!(Velocity::c(), 2))
            .get_tuple(),
            MassUnit::solar_mass => (1.98892, 30),
            MassUnit::earth_mass => (5.9736, 24),
            MassUnit::lunar_mass => (7.348, 22),
            MassUnit::jupiter_mass => (1.89881, 27),
        }
    }
}

impl_const!(Mass, electron, 9.1093837139, -31);
impl_const!(Mass, proton, 1.67262192595, -27);
impl_const!(Mass, neutron, 1.67492750056, -27);

impl_quantity!(Mass, MassUnit, MassUnit::kg);
impl_div_with_self_to_f64!(Mass);
