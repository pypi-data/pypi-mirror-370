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
pub enum VolumeUnit {
    kmcb,
    mcb,
    dmcb,
    l,
    cmcb,
    mmcb,
    mumcb,
    incb,
    ftcb,
    ydcb,
    impgal,
}

impl PhysicsUnit for VolumeUnit {
    fn name(&self) -> &str {
        match self {
            VolumeUnit::kmcb => "km³",
            VolumeUnit::mcb => "m³",
            VolumeUnit::dmcb => "dm³",
            VolumeUnit::l => "l",
            VolumeUnit::cmcb => "cm³",
            VolumeUnit::mmcb => "mm³",
            VolumeUnit::mumcb => "μm³",
            VolumeUnit::incb => "in³",
            VolumeUnit::ftcb => "ft³",
            VolumeUnit::ydcb => "yd³",
            VolumeUnit::impgal => "imp gal",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            VolumeUnit::kmcb => (1.0, 9),
            VolumeUnit::mcb => (1.0, 0),
            VolumeUnit::dmcb => (1.0, -3),
            VolumeUnit::l => (1.0, -3),
            VolumeUnit::cmcb => (1.0, -6),
            VolumeUnit::mmcb => (1.0, -9),
            VolumeUnit::mumcb => (1.0, -18),
            VolumeUnit::incb => (1.6387064, -5),
            VolumeUnit::ftcb => (2.8316846592, -2),
            VolumeUnit::ydcb => (7.64554857984, -1),
            VolumeUnit::impgal => (3.78541, -3),
        }
    }
}

impl_quantity!(Volume, VolumeUnit, VolumeUnit::dmcb);
impl_div_with_self_to_f64!(Volume);
