use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::{FromPrimitive, Zero};
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};

#[macro_export]
macro_rules! power {
    ($x:expr, 1) => {
        $x
    };
    ($x:expr, 2) => {
        $x * $x
    };
    ($x:expr, 3) => {
        $x * $x * $x
    };
    ($x:expr, 4) => {
        $x * $x * $x * $x
    };
    ($x:expr, 5) => {
        $x * $x * $x * $x * $x
    };
    ($x:expr, 6) => {
        $x * $x * $x * $x * $x * $x
    };
}

pub trait MulArray1<RHS> {
    type Output;

    fn mul_array1(self, rhs: Array1<RHS>) -> Self::Output;
}

pub trait MulArray2<RHS> {
    type Output;

    fn mul_array2(self, rhs: Array2<RHS>) -> Result<Self::Output, String>;
}

pub trait DivArray1<RHS> {
    type Output;

    fn div_array1(self, rhs: Array1<RHS>) -> Self::Output;
}

pub trait DivArray2<RHS> {
    type Output;

    fn div_array2(self, rhs: Array2<RHS>) -> Result<Self::Output, String>;
}

pub trait QuantityArray2<T> {
    fn from_raw(raw: ArrayView2<f64>, unit: T) -> Self;
    fn to_raw(&self) -> Array2<f64>;
    fn to(&self, unit: T) -> Array2<f64>;
}

pub trait QuantityArray1<T> {
    fn from_raw(raw: ArrayView1<f64>, unit: T) -> Self;
    fn to_raw(&self) -> Array1<f64>;
    fn to(&self, unit: T) -> Array1<f64>;
}

pub trait PhysicsQuantity:
    Copy
    + FromPrimitive
    + Zero
    + Add<Output = Self>
    + AddAssign
    + Div<f64, Output = Self>
    + DivAssign<f64>
    + Mul<f64, Output = Self>
    + MulAssign<f64>
    + Sub<Output = Self>
    + SubAssign
    + PartialOrd
    + Neg<Output = Self>
    + From<f64>
{
    fn as_f64(&self) -> f64;
    type Unit: PhysicsUnit;
    fn new(value: f64, unit: Self::Unit) -> Self;
    fn to(&self, unit: Self::Unit) -> f64;
    fn get_tuple(&self) -> (f64, i32);
    fn abs(self) -> Self;
    fn from_raw(value: f64) -> Self;
    fn from_exponential(multiplier: f64, power: i32) -> Self;
    fn min(self, other: Self) -> Self;
    fn max(self, other: Self) -> Self;
    #[deprecated(since = "0.2.9", note = "please use `as_f64()` instead")]
    fn to_raw(&self) -> f64 {
        self.as_f64()
    }
    #[deprecated(since = "0.2.9", note = "please use `as_f64()` instead")]
    fn get_value(&self) -> f64 {
        self.as_f64()
    }
    fn get_power(&self) -> i32;
    fn get_multiplier(&self) -> f64;
    fn split_value(v: f64) -> (f64, i32);
    fn is_close(&self, other: &Self, tolerance: &Self) -> bool;
    fn optimize(&mut self);
    fn is_nan(&self) -> bool;
    const INFINITY: Self;
    const NEG_INFINITY: Self;
}

pub trait Sqrt<T> {
    fn sqrt(self) -> T;
}

impl PhysicsQuantity for f64 {
    fn as_f64(&self) -> f64 {
        *self
    }

    type Unit = NoUnit;

    fn new(value: f64, _unit: Self::Unit) -> Self {
        value
    }

    fn to(&self, _unit: Self::Unit) -> f64 {
        self.as_f64()
    }

    fn get_tuple(&self) -> (f64, i32) {
        (self.get_multiplier(), self.get_power())
    }

    fn abs(self) -> Self {
        self.abs()
    }

    fn is_nan(&self) -> bool {
        f64::is_nan(*self)
    }
    
    fn from_raw(value: f64) -> Self {
        value
    }

    fn from_exponential(multiplier: f64, power: i32) -> Self {
        multiplier * 10_f64.powi(power)
    }

    fn min(self, other: Self) -> Self {
        if self < other {
            self
        } else {
            other
        }
    }

    fn max(self, other: Self) -> Self {
        if self > other {
            self
        } else {
            other
        }
    }
    fn get_power(&self) -> i32 {
        0
    }

    fn get_multiplier(&self) -> f64 {
        *self
    }

    fn split_value(v: f64) -> (f64, i32) {
        let power = v.abs().log10().floor() as i32;
        let multiplier = v / 10f64.powi(power);
        (multiplier, power)
    }

    fn is_close(&self, other: &Self, tolerance: &Self) -> bool {
        (self - other).abs() < (*tolerance)
    }

    fn optimize(&mut self) {}

    const INFINITY: Self = f64::INFINITY;
    const NEG_INFINITY: Self = f64::NEG_INFINITY;
}
pub use crate::power;

pub trait PhysicsUnit {
    fn name(&self) -> &str;
    fn base_per_x(&self) -> (f64, i32);
}

pub enum NoUnit {
    no_unit,
}

impl PhysicsUnit for NoUnit {
    fn name(&self) -> &str {
        ""
    }

    fn base_per_x(&self) -> (f64, i32) {
        (1., 0)
    }
}
