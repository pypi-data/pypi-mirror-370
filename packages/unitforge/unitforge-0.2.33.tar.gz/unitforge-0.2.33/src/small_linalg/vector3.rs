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
pub struct Vector3<T: PhysicsQuantity> {
    pub data: [T; 3],
}

impl<T> Neg for Vector3<T>
where
    T: PhysicsQuantity + Neg<Output = T>,
{
    type Output = Self;

    fn neg(self) -> Self::Output {
        Vector3 {
            data: [self.data[0].neg(), self.data[1].neg(), self.data[2].neg()],
        }
    }
}

impl<T: PhysicsQuantity + Zero> Zero for Vector3<T> {
    fn zero() -> Self {
        Vector3::new([T::zero(), T::zero(), T::zero()])
    }

    fn is_zero(&self) -> bool {
        self.data[0].is_zero() && self.data[1].is_zero() && self.data[2].is_zero()
    }
}

impl<T: PhysicsQuantity + Display> Display for Vector3<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}\n{}\n{}", self.data[0], self.data[1], self.data[2])
    }
}

impl<T, U, V> Mul<U> for Vector3<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector3<V>;

    fn mul(self, scalar: U) -> Vector3<V> {
        Vector3 {
            data: [
                self.data[0] * scalar,
                self.data[1] * scalar,
                self.data[2] * scalar,
            ],
        }
    }
}

impl<T, U, V> Mul<Vector3<U>> for Vector3<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector3<V>;

    fn mul(self, other: Vector3<U>) -> Vector3<V> {
        Vector3 {
            data: [
                self.data[0] * other.data[0],
                self.data[1] * other.data[1],
                self.data[2] * other.data[2],
            ],
        }
    }
}

impl<T: PhysicsQuantity> MulAssign<f64> for Vector3<T> {
    fn mul_assign(&mut self, scalar: f64) {
        self.data[0] *= scalar;
        self.data[1] *= scalar;
        self.data[2] *= scalar;
    }
}

impl<T, U, V> Div<U> for Vector3<T>
where
    T: PhysicsQuantity + Div<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Vector3<V>;

    fn div(self, scalar: U) -> Vector3<V> {
        Vector3 {
            data: [
                self.data[0] / scalar,
                self.data[1] / scalar,
                self.data[2] / scalar,
            ],
        }
    }
}

impl<T: PhysicsQuantity> DivAssign<f64> for Vector3<T> {
    fn div_assign(&mut self, scalar: f64) {
        self.data[0] /= scalar;
        self.data[1] /= scalar;
        self.data[2] /= scalar;
    }
}

impl<T: PhysicsQuantity> Add for Vector3<T> {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            data: [
                self.data[0] + other.data[0],
                self.data[1] + other.data[1],
                self.data[2] + other.data[2],
            ],
        }
    }
}

impl<T: PhysicsQuantity> AddAssign for Vector3<T> {
    fn add_assign(&mut self, other: Self) {
        self.data[0] += other.data[0];
        self.data[1] += other.data[1];
        self.data[2] += other.data[2];
    }
}

impl<T: PhysicsQuantity> Sub for Vector3<T> {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        Self {
            data: [
                self.data[0] - other.data[0],
                self.data[1] - other.data[1],
                self.data[2] - other.data[2],
            ],
        }
    }
}

impl<T: PhysicsQuantity> SubAssign for Vector3<T> {
    fn sub_assign(&mut self, other: Self) {
        self.data[0] -= other.data[0];
        self.data[1] -= other.data[1];
        self.data[2] -= other.data[2];
    }
}

impl<T: PhysicsQuantity> Vector3<T> {
    pub fn from_ndarray(array: ArrayView1<T>) -> Result<Self, String> {
        if array.len() == 3 {
            let data = [array[0], array[1], array[2]];
            Ok(Vector3 { data })
        } else {
            Err(format!("Array length is not 3, it is {}", array.len()))
        }
    }
}

impl Vector3<f64> {
    pub fn x() -> Self {
        Self {
            data: [1.0, 0.0, 0.0],
        }
    }

    pub fn y() -> Self {
        Self {
            data: [0.0, 1.0, 0.0],
        }
    }

    pub fn z() -> Self {
        Self {
            data: [0.0, 0.0, 1.0],
        }
    }
}

impl<T: PhysicsQuantity> Vector3<T> {
    pub fn new(data: [T; 3]) -> Self {
        Self { data }
    }

    pub fn zero() -> Self {
        Self {
            data: [T::zero(); 3],
        }
    }

    pub fn data(&self) -> [T; 3] {
        self.data
    }

    pub fn from_f64(data: [f64; 3]) -> Self {
        let mut quantity_data = [T::zero(); 3];
        quantity_data[0] = T::from_raw(data[0]);
        quantity_data[1] = T::from_raw(data[1]);
        quantity_data[2] = T::from_raw(data[2]);
        Self::new(quantity_data)
    }

    pub fn to_ndarray(&self) -> Array1<T> {
        Array1::from_vec(self.data.to_vec())
    }

    pub fn norm(&self) -> T {
        T::from_raw(
            (self.data[0].as_f64() * self.data[0].as_f64()
                + self.data[1].as_f64() * self.data[1].as_f64()
                + self.data[2].as_f64() * self.data[2].as_f64())
            .sqrt(),
        )
    }

    pub fn abs(&self) -> Self {
        Self {
            data: [self.data[0].abs(), self.data[1].abs(), self.data[2].abs()],
        }
    }

    pub fn to_unit_vector(&self) -> Vector3<f64> {
        let len = self.norm();
        if len.is_zero() {
            return Vector3::zero();
        }
        self.as_f64() / len.as_f64()
    }

    #[deprecated(since = "0.2.9", note = "please use `as_f64()` instead")]
    pub fn to_raw(&self) -> Vector3<f64> {
        self.as_f64()
    }
    pub fn as_f64(&self) -> Vector3<f64> {
        Vector3::new([
            self.data()[0].as_f64(),
            self.data()[1].as_f64(),
            self.data()[2].as_f64(),
        ])
    }

    pub fn from_raw(raw: Vector3<f64>) -> Self {
        Self {
            data: [
                T::from_raw(raw[0]),
                T::from_raw(raw[1]),
                T::from_raw(raw[2]),
            ],
        }
    }

    pub fn optimize(&mut self) {
        for element in &mut self.data {
            element.optimize();
        }
    }
}

impl<T: PhysicsQuantity> Vector3<T> {
    pub fn cross<U, V>(&self, b: &Vector3<U>) -> Vector3<V>
    where
        T: Mul<U, Output = V>,
        U: PhysicsQuantity,
        V: PhysicsQuantity + Sub<Output = V>,
    {
        Vector3::new([
            self.data[1] * b.data[2] - self.data[2] * b.data[1],
            self.data[2] * b.data[0] - self.data[0] * b.data[2],
            self.data[0] * b.data[1] - self.data[1] * b.data[0],
        ])
    }
}

impl<T: PhysicsQuantity> Vector3<T> {
    pub fn dot_vct<U, V>(&self, other: &Vector3<U>) -> V
    where
        T: Mul<U, Output = V>,
        U: PhysicsQuantity,
        V: PhysicsQuantity + Add<Output = V>,
    {
        self.data[0] * other.data[0] + self.data[1] * other.data[1] + self.data[2] * other.data[2]
    }
}

impl<T: PhysicsQuantity> Index<usize> for Vector3<T> {
    type Output = T;

    fn index(&self, index: usize) -> &Self::Output {
        &self.data[index]
    }
}

impl<T: PhysicsQuantity> IndexMut<usize> for Vector3<T> {
    fn index_mut(&mut self, index: usize) -> &mut Self::Output {
        &mut self.data[index]
    }
}
