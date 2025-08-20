use crate::{small_linalg::Vector2, PhysicsQuantity};
use std::ops::{Add, AddAssign, Div, Index, IndexMut, Mul, Neg, Sub, SubAssign};

#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Matrix2<T: PhysicsQuantity> {
    data: [[T; 2]; 2],
}

impl<T: PhysicsQuantity> Matrix2<T> {
    pub fn new(data: [[T; 2]; 2]) -> Self {
        Self { data }
    }

    pub fn zero() -> Self {
        Self {
            data: [[T::zero(); 2]; 2],
        }
    }

    pub fn from_f64(data: [[f64; 2]; 2]) -> Self {
        let mut qd = [[T::zero(); 2]; 2];
        for i in 0..2 {
            for j in 0..2 {
                qd[i][j] = T::from_raw(data[i][j]);
            }
        }
        Self::new(qd)
    }

    pub fn data(&self) -> [[T; 2]; 2] {
        self.data
    }

    pub fn to_f64(&self) -> Matrix2<f64> {
        Matrix2::new([
            [self.data[0][0].as_f64(), self.data[0][1].as_f64()],
            [self.data[1][0].as_f64(), self.data[1][1].as_f64()],
        ])
    }

    pub fn get_column(&self, col: usize) -> Vector2<T> {
        assert!(col < 2);
        Vector2::new([self.data[0][col], self.data[1][col]])
    }

    pub fn get_row(&self, row: usize) -> Vector2<T> {
        assert!(row < 2);
        Vector2::new(self.data[row])
    }

    pub fn transpose(&self) -> Matrix2<T> {
        Matrix2::new([
            [self.data[0][0], self.data[1][0]],
            [self.data[0][1], self.data[1][1]],
        ])
    }

    pub fn frobenius_norm(&self) -> T {
        let mut acc = 0.0;
        for i in 0..2 {
            for j in 0..2 {
                acc += 10_f64.powi(self.data[i][j].get_power() * 2)
                    * self.data[i][j].get_multiplier().powi(2);
            }
        }
        T::from_raw(acc.sqrt())
    }

    pub fn optimize(&mut self) {
        for row in &mut self.data {
            for value in row {
                value.optimize();
            }
        }
    }

    pub fn abs(&self) -> Self {
        Self {
            data: [
                [self.data[0][0].abs(), self.data[0][1].abs()],
                [self.data[1][0].abs(), self.data[1][1].abs()],
            ],
        }
    }
}

impl<T: PhysicsQuantity> Index<(usize, usize)> for Matrix2<T> {
    type Output = T;

    fn index(&self, index: (usize, usize)) -> &T {
        &self.data[index.0][index.1]
    }
}

impl<T: PhysicsQuantity> IndexMut<(usize, usize)> for Matrix2<T> {
    fn index_mut(&mut self, index: (usize, usize)) -> &mut T {
        &mut self.data[index.0][index.1]
    }
}

impl<T: PhysicsQuantity + Neg<Output = T>> Neg for Matrix2<T> {
    type Output = Self;
    fn neg(self) -> Self::Output {
        Matrix2::new([
            [self.data[0][0].neg(), self.data[0][1].neg()],
            [self.data[1][0].neg(), self.data[1][1].neg()],
        ])
    }
}

impl<T: PhysicsQuantity + Add<Output = T>> Add for Matrix2<T> {
    type Output = Self;
    fn add(self, rhs: Self) -> Self::Output {
        Matrix2::new([
            [
                self.data[0][0] + rhs.data[0][0],
                self.data[0][1] + rhs.data[0][1],
            ],
            [
                self.data[1][0] + rhs.data[1][0],
                self.data[1][1] + rhs.data[1][1],
            ],
        ])
    }
}

impl<T: PhysicsQuantity + Sub<Output = T>> Sub for Matrix2<T> {
    type Output = Self;
    fn sub(self, rhs: Self) -> Self::Output {
        Matrix2::new([
            [
                self.data[0][0] - rhs.data[0][0],
                self.data[0][1] - rhs.data[0][1],
            ],
            [
                self.data[1][0] - rhs.data[1][0],
                self.data[1][1] - rhs.data[1][1],
            ],
        ])
    }
}

impl<T: PhysicsQuantity + AddAssign> AddAssign for Matrix2<T> {
    fn add_assign(&mut self, rhs: Self) {
        for i in 0..2 {
            for j in 0..2 {
                self[(i, j)] += rhs[(i, j)];
            }
        }
    }
}

impl<T: PhysicsQuantity + SubAssign> SubAssign for Matrix2<T> {
    fn sub_assign(&mut self, rhs: Self) {
        for i in 0..2 {
            for j in 0..2 {
                self[(i, j)] -= rhs[(i, j)];
            }
        }
    }
}

impl<T, U, V> Mul<U> for Matrix2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Matrix2<V>;

    fn mul(self, scalar: U) -> Self::Output {
        Matrix2::new([
            [self.data[0][0] * scalar, self.data[0][1] * scalar],
            [self.data[1][0] * scalar, self.data[1][1] * scalar],
        ])
    }
}

impl<T: PhysicsQuantity> Matrix2<T> {
    #[inline(always)]
    pub fn dot<U, V>(&self, vec: &Vector2<U>) -> Vector2<V>
    where
        T: Mul<U, Output = V>,
        U: PhysicsQuantity,
        V: PhysicsQuantity + Add<Output = V>,
    {
        let result = [
            self.data[0][0] * vec.data[0] + self.data[0][1] * vec.data[1],
            self.data[1][0] * vec.data[0] + self.data[1][1] * vec.data[1],
        ];
        Vector2::new(result)
    }
}

impl<T, U: PhysicsQuantity> Matrix2<T>
where
    T: PhysicsQuantity + Mul<Output = U>,
    U: Add<Output = U> + Sub<Output = U>,
{
    #[inline(always)]
    pub fn det(&self) -> U {
        self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]
    }
}

impl<T, U, V, R> Matrix2<T>
where
    T: PhysicsQuantity + Mul<T, Output = U> + Mul<U, Output = V> + Div<U, Output = R>,
    U: PhysicsQuantity + Mul<T, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
    R: PhysicsQuantity,
{
    pub fn inverse(&self) -> Option<Matrix2<R>> {
        let det = self.det();

        if det.as_f64().abs() < f64::EPSILON {
            return None;
        }

        Some(Matrix2::new([
            [self[(1, 1)] / det, -self[(0, 1)] / det],
            [-self[(1, 0)] / det, self[(0, 0)] / det],
        ]))
    }
}
