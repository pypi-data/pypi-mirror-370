use crate::prelude::*;
use crate::quantities::*;
use crate::{
    impl_div, impl_mul, impl_mul_relation_with_other, impl_mul_relation_with_self,
    impl_mul_with_self, impl_sqrt,
};
use ndarray::{Array1, Array2};
#[cfg(feature = "pyo3")]
use pyo3::pymethods;

impl_mul_relation_with_other!(Acceleration, Time, Velocity);
impl_mul_relation_with_other!(Acceleration, Mass, Force);
impl_mul_relation_with_other!(AngularVelocity, Time, Angle);
impl_mul_relation_with_other!(AngularVelocity, Distance, Velocity);
impl_mul_relation_with_other!(AngularAcceleration, Time, AngularVelocity);
impl_mul_relation_with_other!(Area, Stress, Force);
impl_mul_relation_with_other!(InverseDistance, Volume, Area);
impl_mul_relation_with_other!(InverseArea, AreaOfMoment, Area);
impl_mul_relation_with_other!(Distance, Volume, AreaOfMoment);
impl_mul_relation_with_other!(Compliance, Force, Distance);
impl_mul_relation_with_other!(Compliance, ForceArea, Volume);
impl_mul_relation_with_other!(Density, Volume, Mass);
impl_mul_relation_with_other!(Distance, Area, Volume);
impl_mul_relation_with_other!(Distance, Stiffness, Force);
impl_mul_relation_with_other!(Distance, InverseArea, InverseDistance);
impl_mul_relation_with_other!(InverseDistance, Area, Distance);
impl_mul_relation_with_other!(Velocity, Time, Distance);
impl_mul_relation_with_other!(Force, Distance, ForceDistance);
impl_mul_relation_with_other!(Force, Area, ForceArea);
impl_mul_relation_with_other!(ForceArea, Distance, ForceVolume);
impl_mul_relation_with_other!(AreaOfMoment, Stress, ForceArea);
impl_mul_relation_with_other!(ForceDistance, Distance, ForceArea);
impl_mul_relation_with_other!(Mass, VelocitySquared, ForceDistance);
impl_mul_relation_with_other!(Voltage, Charge, ForceDistance);
impl_mul_relation_with_other!(Stress, Volume, ForceDistance);
impl_mul_relation_with_other!(ForcePerDistancePowerFour, Volume, Stiffness);
impl_mul_relation_with_other!(ForcePerVolume, InverseDistance, ForcePerDistancePowerFour);
impl_mul_relation_with_other!(ForcePerVolume, Volume, Force);
impl_mul_relation_with_other!(Density, Acceleration, ForcePerVolume);
impl_mul_relation_with_other!(ForcePerVolume, Area, Stiffness);
impl_mul_relation_with_other!(ForcePerVolume, Distance, Stress);
impl_mul_relation_with_other!(InverseDistance, Stress, ForcePerVolume);
impl_mul_relation_with_other!(InverseDistance, ForceDistance, Force);
impl_mul_relation_with_other!(Stress, Distance, Stiffness);
impl_mul_relation_with_other!(Velocity, Distance, Time);
impl_mul_relation_with_other!(MassPerDistance, Distance, Mass);
impl_mul_relation_with_other!(Area, Density, MassPerDistance);
impl_mul_relation_with_other!(MassPerDistance, Acceleration, Stiffness);
impl_mul_relation_with_other!(Stiffness, AreaOfMoment, ForceVolume);

impl_mul_relation_with_self!(Distance, Area);
impl_mul_relation_with_self!(Area, AreaOfMoment);
impl_mul_relation_with_self!(InverseDistance, InverseArea);
impl_mul_relation_with_self!(Stress, StressSquared);
