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
pub enum DensityUnit {
    kg_dmcb,
    kg_mcb,
    g_cmcb,
    g_mcb,
    lb_ftcb,
    lb_incb,
}

impl PhysicsUnit for DensityUnit {
    fn name(&self) -> &str {
        match &self {
            DensityUnit::kg_dmcb => "kg/dm³",
            DensityUnit::kg_mcb => "kg/m³",
            DensityUnit::g_cmcb => "g/cm³",
            DensityUnit::g_mcb => "g/m³",
            DensityUnit::lb_ftcb => "lb/ft³",
            DensityUnit::lb_incb => "lb/in³",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            DensityUnit::kg_dmcb => (1.0, 3),
            DensityUnit::kg_mcb => (1.0, 0),
            DensityUnit::g_cmcb => (1.0, 3),
            DensityUnit::g_mcb => (1.0, -3),
            DensityUnit::lb_ftcb => (1.60185, 1),
            DensityUnit::lb_incb => (2.76799, 4),
        }
    }
}

impl_const!(Density, aluminium, 2.7, 3);
impl_const!(Density, water, 1., 3);
impl_const!(Density, air, 1.225, 0);
impl_const!(Density, steel, 7.78, 3);
impl_const!(Density, graphit, 2.26, 3);
impl_const!(Density, diamant, 3.51, 3);
impl_const!(Density, lithium, 5.34, 2);
impl_const!(Density, chrome, 7.14, 3);
impl_const!(Density, copper, 8.92, 3);
impl_const!(Density, zink, 7.14, 3);
impl_const!(Density, nickel, 8.907, 3);
impl_const!(Density, lead, 1.1342, 4);
impl_const!(Density, beryllium, 1.845, 3);
impl_const!(Density, bor, 2.35, 3);
impl_const!(Density, natrium, 9.68, 2);
impl_const!(Density, magnesium, 1.737, 3);
impl_const!(Density, silicium, 2.336, 3);
impl_const!(Density, sulfur, 2.07, 3);
impl_const!(Density, potassium, 8.56, 2);
impl_const!(Density, scandium, 2.989, 3);
impl_const!(Density, titanium, 4.5, 3);
impl_const!(Density, vanadium, 6.099, 3);
impl_const!(Density, manganese, 7.476, 3);
impl_const!(Density, iron, 7.874, 3);
impl_const!(Density, cobalt, 8.834, 3);
impl_const!(Density, germanium, 5.327, 3);
impl_const!(Density, arsenic, 5.782, 3);
impl_const!(Density, rubidium, 1.534, 3);
impl_const!(Density, yttrium, 4.469, 3);
impl_const!(Density, zirconium, 6.505, 3);
impl_const!(Density, niobium, 8.582, 3);
impl_const!(Density, molybdenum, 1.0223, 4);
impl_const!(Density, ruthenium, 1.2364, 4);
impl_const!(Density, rhodium, 1.2423, 4);
impl_const!(Density, palladium, 1.2007, 4);
impl_const!(Density, silver, 1.0503, 4);
impl_const!(Density, cadmium, 8.649, 3);
impl_const!(Density, indium, 7.290, 3);
impl_const!(Density, tin, 7.31, 3);
impl_const!(Density, antimony, 6.694, 3);
impl_const!(Density, tellurium, 6.237, 3);
impl_const!(Density, iodine, 4.944, 3);
impl_const!(Density, caesium, 1.886, 3);
impl_const!(Density, barium, 3.594, 3);
impl_const!(Density, lutetium, 9.84, 3);
impl_const!(Density, hafnium, 13.281, 3);
impl_const!(Density, tantalum, 16.678, 3);
impl_const!(Density, tungsten, 1.9254, 4);
impl_const!(Density, rhenium, 2.1010, 4);
impl_const!(Density, osmium, 2.2587, 4);
impl_const!(Density, iridium, 2.2562, 4);
impl_const!(Density, platinum, 2.1452, 4);
impl_const!(Density, gold, 1.9283, 4);
impl_const!(Density, mercury, 1.3546, 4);
impl_const!(Density, thallium, 1.1873, 4);
impl_const!(Density, bismuth, 9.807, 3);
impl_const!(Density, polonium, 9.4, 3);
impl_const!(Density, francium, 2.458, 3);
impl_const!(Density, radium, 5.5, 3);
impl_const!(Density, lawrencium, 1.44, 4);
impl_const!(Density, rutherfordium, 1.7, 4);
impl_const!(Density, cerium, 6.7, 3);
impl_const!(Density, praseodymium, 6.773, 3);
impl_const!(Density, neodymium, 7.007, 3);
impl_const!(Density, promethium, 7.2, 3);
impl_const!(Density, samarium, 7.518, 3);
impl_const!(Density, europium, 5.246, 3);
impl_const!(Density, gadolinium, 7.899, 3);
impl_const!(Density, terbium, 8.229, 3);
impl_const!(Density, dysprosium, 8.55, 3);
impl_const!(Density, holmium, 8.795, 3);
impl_const!(Density, erbium, 9.065, 3);
impl_const!(Density, ytterbium, 6.967, 3);
impl_const!(Density, actinium, 1., 4);
impl_const!(Density, protactinium, 1.543, 4);
impl_const!(Density, uranium, 1.905, 4);
impl_const!(Density, neptunium, 2.048, 4);
impl_const!(Density, plutonium, 1.985, 4);
impl_const!(Density, americium, 12., 4);
impl_const!(Density, curium, 13.51, 4);

impl_quantity!(Density, DensityUnit, DensityUnit::kg_dmcb);
impl_div_with_self_to_f64!(Density);
