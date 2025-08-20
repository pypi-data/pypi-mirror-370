use crate::PhysicsQuantity;
use ndarray::{Array1, ArrayView1};
use num_traits::Zero;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::fmt::{Display, Formatter};
use std::ops::{
    Add, AddAssign, Div, DivAssign, Index, IndexMut, Mul, MulAssign, Neg, Sub, SubAssign,
};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Vector2<T: PhysicsQuantity> {
    pub data: [T; 2],
}

impl<T> Neg for Vector2<T>
where
    T: PhysicsQuantity + Neg<Output = T>,
{
    type Output = Self;

    fn neg(self) -> Self::Output {
        Vector2 {
            data: [self.data[0].neg(), self.data[1].neg()],
        }
    }
}

impl<T: PhysicsQuantity + Zero> Zero for Vector2<T> {
    fn zero() -> Self {
        Vector2::new([T::zero(), T::zero()])
    }

    fn is_zero(&self) -> bool {
        self.data[0].is_zero() && self.data[1].is_zero()
    }
}

impl<T: PhysicsQuantity + Display> Display for Vector2<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}\n{}", self.data[0], self.data[1])
    }
}

impl<T, U, V> Mul<U> for Vector2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector2<V>;

    fn mul(self, scalar: U) -> Vector2<V> {
        Vector2 {
            data: [self.data[0] * scalar, self.data[1] * scalar],
        }
    }
}

impl<T, U, V> Mul<Vector2<U>> for Vector2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector2<V>;

    fn mul(self, other: Vector2<U>) -> Vector2<V> {
        Vector2 {
            data: [self.data[0] * other.data[0], self.data[1] * other.data[1]],
        }
    }
}

impl<T: PhysicsQuantity> MulAssign<f64> for Vector2<T> {
    fn mul_assign(&mut self, scalar: f64) {
        self.data[0] *= scalar;
        self.data[1] *= scalar;
    }
}

impl<T, U, V> Div<U> for Vector2<T>
where
    T: PhysicsQuantity + Div<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector2<V>;

    fn div(self, scalar: U) -> Vector2<V> {
        Vector2 {
            data: [self.data[0] / scalar, self.data[1] / scalar],
        }
    }
}

impl<T: PhysicsQuantity> DivAssign<f64> for Vector2<T> {
    fn div_assign(&mut self, scalar: f64) {
        self.data[0] /= scalar;
        self.data[1] /= scalar;
    }
}

impl<T: PhysicsQuantity> Add for Vector2<T> {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            data: [self.data[0] + other.data[0], self.data[1] + other.data[1]],
        }
    }
}

impl<T: PhysicsQuantity> AddAssign for Vector2<T> {
    fn add_assign(&mut self, other: Self) {
        self.data[0] += other.data[0];
        self.data[1] += other.data[1];
    }
}

impl<T: PhysicsQuantity> Sub for Vector2<T> {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        Self {
            data: [self.data[0] - other.data[0], self.data[1] - other.data[1]],
        }
    }
}

impl<T: PhysicsQuantity> SubAssign for Vector2<T> {
    fn sub_assign(&mut self, other: Self) {
        self.data[0] -= other.data[0];
        self.data[1] -= other.data[1];
    }
}

impl<T: PhysicsQuantity> Vector2<T> {
    pub fn new(data: [T; 2]) -> Self {
        Self { data }
    }

    pub fn zero() -> Self {
        Self {
            data: [T::zero(); 2],
        }
    }

    pub fn data(&self) -> [T; 2] {
        self.data
    }

    pub fn from_f64(data: [f64; 2]) -> Self {
        let mut quantity_data = [T::zero(); 2];
        quantity_data[0] = T::from_raw(data[0]);
        quantity_data[1] = T::from_raw(data[1]);
        Self::new(quantity_data)
    }

    pub fn to_ndarray(&self) -> Array1<T> {
        Array1::from_vec(self.data.to_vec())
    }

    pub fn from_ndarray(array: ArrayView1<T>) -> Result<Self, String> {
        if array.len() == 2 {
            Ok(Vector2 {
                data: [array[0], array[1]],
            })
        } else {
            Err(format!("Array length is not 2, it is {}", array.len()))
        }
    }

    pub fn norm(&self) -> T {
        T::from_raw((self.data[0].as_f64().powi(2) + self.data[1].as_f64().powi(2)).sqrt())
    }

    pub fn abs(&self) -> Self {
        Self {
            data: [self.data[0].abs(), self.data[1].abs()],
        }
    }

    pub fn to_unit_vector(&self) -> Vector2<f64> {
        let len = self.norm();
        if len.is_zero() {
            return Vector2::zero();
        }
        self.as_f64() / len.as_f64()
    }

    pub fn as_f64(&self) -> Vector2<f64> {
        Vector2::new([self.data[0].as_f64(), self.data[1].as_f64()])
    }

    pub fn from_raw(raw: Vector2<f64>) -> Self {
        Self {
            data: [T::from_raw(raw[0]), T::from_raw(raw[1])],
        }
    }

    pub fn optimize(&mut self) {
        for element in &mut self.data {
            element.optimize();
        }
    }

    pub fn dot_vct<U, V>(&self, other: &Vector2<U>) -> V
    where
        T: Mul<U, Output = V>,
        U: PhysicsQuantity,
        V: PhysicsQuantity + Add<Output = V>,
    {
        self.data[0] * other.data[0] + self.data[1] * other.data[1]
    }
}

impl Vector2<f64> {
    pub fn x() -> Self {
        Self { data: [1.0, 0.0] }
    }

    pub fn y() -> Self {
        Self { data: [0.0, 1.0] }
    }
}

impl<T: PhysicsQuantity> Index<usize> for Vector2<T> {
    type Output = T;

    fn index(&self, index: usize) -> &Self::Output {
        &self.data[index]
    }
}

impl<T: PhysicsQuantity> IndexMut<usize> for Vector2<T> {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.data[index]
    }
}
