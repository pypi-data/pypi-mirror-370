#![allow(non_camel_case_types)]
pub mod impl_macros;
pub use impl_macros::*;

pub mod prelude;
mod relations;

include!(concat!(env!("OUT_DIR"), "/quantities.rs"));
#[cfg(feature = "pyo3")]
include!(concat!(env!("OUT_DIR"), "/vector3_py.rs"));
#[cfg(feature = "pyo3")]
include!(concat!(env!("OUT_DIR"), "/matrix3_py.rs"));
#[cfg(feature = "pyo3")]
include!(concat!(env!("OUT_DIR"), "/python_module_definition.rs"));

pub use prelude::*;

pub mod quantities {
    pub mod acceleration;
    pub use acceleration::*;
    pub mod angle;
    pub use angle::*;
    pub mod angular_acceleration;
    pub use angular_acceleration::*;
    pub mod angular_velocity;
    pub use angular_velocity::*;
    pub mod area;
    pub use area::*;
    pub mod area_of_moment;
    pub use area_of_moment::*;
    pub mod charge;
    pub use charge::*;
    pub mod compliance;
    pub use compliance::*;
    pub mod density;
    pub use density::*;
    pub mod distance;
    pub use distance::*;
    pub mod force;
    pub use force::*;
    pub mod force_area;
    pub use force_area::*;
    pub mod force_div_distance_power_four;
    pub use force_div_distance_power_four::*;
    pub mod force_per_volume;
    pub use force_per_volume::*;
    pub mod force_volume;
    pub use force_volume::*;
    pub mod inverse_distance;
    pub use inverse_distance::*;
    pub mod inverse_area;
    pub use inverse_area::*;
    pub mod mass;
    pub use mass::*;
    pub mod mass_per_distance;
    pub use mass_per_distance::*;
    pub mod force_distance;
    pub use force_distance::*;
    pub mod stiffness;
    pub use stiffness::*;
    pub mod strain;
    pub use strain::*;
    pub mod stress;
    pub use stress::*;
    pub mod stress_squared;
    pub use stress_squared::*;
    pub mod time;
    pub use time::*;
    pub mod velocity;
    pub use velocity::*;
    pub mod velocity_squared;
    pub use velocity_squared::*;
    pub mod volume;
    pub use volume::*;
    pub mod voltage;
    pub use voltage::*;
}
pub use quantities::*;

pub mod small_linalg {
    pub mod vector3;
    pub use vector3::*;
    pub mod vector2;
    pub use vector2::*;
    pub mod matrix3;
    pub use matrix3::*;
    pub mod matrix2;
    pub use matrix2::*;
    pub mod matrix2x3;
    pub use matrix2x3::*;
    pub mod matrix3x2;
    pub use matrix3x2::*;
}

#[cfg(test)]
pub mod tests {
    pub mod quantity_unit_tests;
    #[cfg(feature = "serde")]
    pub mod serde_tests;
}
