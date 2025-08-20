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
pub enum ForceDistanceUnit {
    Nm,
    Ndm,
    Ncm,
    Nmm,
    kNm,
    kNdm,
    kNcm,
    kNmm,
    LbFt,
    LbIn,
    J,
    eV,
    keV,
    MeV,
    GeV,
    TeV,
}

impl PhysicsUnit for ForceDistanceUnit {
    fn name(&self) -> &str {
        match self {
            ForceDistanceUnit::Nm => "Nm",
            ForceDistanceUnit::Ndm => "Ndm",
            ForceDistanceUnit::Ncm => "Ncm",
            ForceDistanceUnit::Nmm => "Nmm",
            ForceDistanceUnit::kNm => "kNm",
            ForceDistanceUnit::kNdm => "kNdm",
            ForceDistanceUnit::kNcm => "kNcm",
            ForceDistanceUnit::kNmm => "kNmm",
            ForceDistanceUnit::LbFt => "lb-ft",
            ForceDistanceUnit::LbIn => "lb-in",
            ForceDistanceUnit::J => "J",
            ForceDistanceUnit::eV => "eV",
            ForceDistanceUnit::keV => "keV",
            ForceDistanceUnit::MeV => "MeV",
            ForceDistanceUnit::GeV => "GeV",
            ForceDistanceUnit::TeV => "TeV",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ForceDistanceUnit::Nmm => (1., -3),
            ForceDistanceUnit::Ncm => (1., -2),
            ForceDistanceUnit::Ndm => (1., -1),
            ForceDistanceUnit::Nm => (1., 0),
            ForceDistanceUnit::kNm => (1., 3),
            ForceDistanceUnit::kNdm => (1., 2),
            ForceDistanceUnit::kNcm => (1., 1),
            ForceDistanceUnit::kNmm => (1., 0),
            ForceDistanceUnit::LbFt => (1.35582, 0),
            ForceDistanceUnit::LbIn => (1.12985, -1),
            ForceDistanceUnit::J => (1.0, 0),
            ForceDistanceUnit::eV => (Charge::e() * Voltage::new(1., VoltageUnit::V)).get_tuple(),
            ForceDistanceUnit::keV => (Charge::e() * Voltage::new(1., VoltageUnit::kV)).get_tuple(),
            ForceDistanceUnit::MeV => (Charge::e() * Voltage::new(1., VoltageUnit::MV)).get_tuple(),
            ForceDistanceUnit::GeV => (Charge::e() * Voltage::new(1., VoltageUnit::GV)).get_tuple(),
            ForceDistanceUnit::TeV => (Charge::e() * Voltage::new(1., VoltageUnit::TV)).get_tuple(),
        }
    }
}

impl_quantity!(ForceDistance, ForceDistanceUnit, ForceDistanceUnit::Nm);
impl_div_with_self_to_f64!(ForceDistance);
