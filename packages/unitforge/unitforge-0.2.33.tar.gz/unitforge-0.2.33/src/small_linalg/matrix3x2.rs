use crate::small_linalg::{Matrix2, Matrix2x3, Matrix3, Vector3};
use crate::{small_linalg::Vector2, PhysicsQuantity};
use std::ops::{Add, Div, Index, IndexMut, Mul, Neg, Sub};

#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Matrix3x2<T: PhysicsQuantity> {
    pub data: [[T; 2]; 3],
}

impl<T: PhysicsQuantity> Matrix3x2<T> {
    pub fn new(data: [[T; 2]; 3]) -> Self {
        Self { data }
    }

    pub fn zero() -> Self {
        Self {
            data: [[T::zero(); 2]; 3],
        }
    }

    pub fn from_f64(data: [[f64; 2]; 3]) -> Self {
        let mut converted = [[T::zero(); 2]; 3];
        for i in 0..3 {
            for j in 0..2 {
                converted[i][j] = T::from_raw(data[i][j]);
            }
        }
        Self::new(converted)
    }

    pub fn as_f64(&self) -> Matrix3x2<f64> {
        Matrix3x2::new([
            [self.data[0][0].as_f64(), self.data[0][1].as_f64()],
            [self.data[1][0].as_f64(), self.data[1][1].as_f64()],
            [self.data[2][0].as_f64(), self.data[2][1].as_f64()],
        ])
    }

    pub fn transpose(&self) -> Matrix2x3<T> {
        Matrix2x3::new([
            [self.data[0][0], self.data[1][0], self.data[2][0]],
            [self.data[0][1], self.data[1][1], self.data[2][1]],
        ])
    }

    pub fn column(&self, i: usize) -> Vector3<T> {
        assert!(i < 2);
        Vector3::new([self.data[0][i], self.data[1][i], self.data[2][i]])
    }

    pub fn row(&self, i: usize) -> Vector2<T> {
        assert!(i < 2);
        Vector2::new(self.data[i])
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
                [self.data[2][0].abs(), self.data[2][1].abs()],
            ],
        }
    }
}

impl<T: PhysicsQuantity + Neg<Output = T>> Neg for Matrix3x2<T> {
    type Output = Self;
    fn neg(self) -> Self {
        Self::new([
            [-self.data[0][0], -self.data[0][1]],
            [-self.data[1][0], -self.data[1][1]],
            [-self.data[2][0], -self.data[2][1]],
        ])
    }
}

impl<T: PhysicsQuantity + Add<Output = T>> Add for Matrix3x2<T> {
    type Output = Self;

    fn add(self, rhs: Self) -> Self {
        let mut out = [[T::zero(); 2]; 3];
        for (i, row) in out.iter_mut().enumerate() {
            for (j, val) in row.iter_mut().enumerate() {
                *val = self.data[i][j] + rhs.data[i][j];
            }
        }
        Self::new(out)
    }
}

impl<T: PhysicsQuantity + Sub<Output = T>> Sub for Matrix3x2<T> {
    type Output = Self;

    fn sub(self, rhs: Self) -> Self {
        let mut out = [[T::zero(); 2]; 3];
        for (i, row) in out.iter_mut().enumerate() {
            for (j, val) in row.iter_mut().enumerate() {
                *val = self.data[i][j] - rhs.data[i][j];
            }
        }
        Self::new(out)
    }
}

impl<T: PhysicsQuantity> Index<(usize, usize)> for Matrix3x2<T> {
    type Output = T;
    fn index(&self, idx: (usize, usize)) -> &Self::Output {
        &self.data[idx.0][idx.1]
    }
}

impl<T: PhysicsQuantity> IndexMut<(usize, usize)> for Matrix3x2<T> {
    fn index_mut(&mut self, idx: (usize, usize)) -> &mut Self::Output {
        &mut self.data[idx.0][idx.1]
    }
}

impl<T: PhysicsQuantity> Matrix3x2<T> {
    pub fn dot_vector2<U, V>(&self, vec: &Vector2<U>) -> Vector3<V>
    where
        U: PhysicsQuantity,
        V: PhysicsQuantity + Add<Output = V>,
        T: Mul<U, Output = V>,
    {
        let r0 = self.data[0][0] * vec[0] + self.data[0][1] * vec[1];
        let r1 = self.data[1][0] * vec[0] + self.data[1][1] * vec[1];
        let r2 = self.data[2][0] * vec[0] + self.data[2][1] * vec[1];
        Vector3::new([r0, r1, r2])
    }
}

impl<T, U, V> Mul<Vector2<U>> for Matrix3x2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity + Add<Output = V>,
{
    type Output = Vector3<V>;

    fn mul(self, rhs: Vector2<U>) -> Self::Output {
        self.dot_vector2(&rhs)
    }
}

impl<T, U, V> Mul<Matrix3x2<U>> for Matrix3<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity + Add<Output = V>,
{
    type Output = Matrix3x2<V>;

    fn mul(self, rhs: Matrix3x2<U>) -> Self::Output {
        let mut result = [[<V as num_traits::Zero>::zero(); 2]; 3];
        for i in 0..3 {
            for j in 0..2 {
                result[i][j] = self[(i, 0)] * rhs[(0, j)]
                    + self[(i, 1)] * rhs[(1, j)]
                    + self[(i, 2)] * rhs[(2, j)];
            }
        }
        Matrix3x2::new(result)
    }
}

impl<T, U, V> Mul<Matrix2x3<U>> for Matrix3x2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity + Add<Output = V>,
{
    type Output = Matrix3<V>;

    fn mul(self, rhs: Matrix2x3<U>) -> Self::Output {
        let mut result = [[<V as num_traits::Zero>::zero(); 3]; 3];
        for i in 0..3 {
            for j in 0..3 {
                result[i][j] = self[(i, 0)] * rhs[(0, j)] + self[(i, 1)] * rhs[(1, j)];
            }
        }
        Matrix3::new(result)
    }
}

impl<T> Matrix3x2<T>
where
    T: PhysicsQuantity + Copy,
{
    pub fn pseudoinverse<U, D, E, V>(&self) -> Option<Matrix2x3<V>>
    where
        T: Mul<T, Output = U>,
        U: PhysicsQuantity + Copy + Mul<U, Output = D> + Div<D, Output = E>,

        D: PhysicsQuantity + Copy + Sub<Output = D>,
        E: PhysicsQuantity + Copy,

        E: Mul<T, Output = V>,
        V: PhysicsQuantity + Copy + Add<Output = V>,
    {
        let a_t: Matrix2x3<T> = self.transpose();
        let a_ta: Matrix2<U> = a_t * *self;

        let det: D = a_ta[(0, 0)] * a_ta[(1, 1)] - a_ta[(0, 1)] * a_ta[(1, 0)];
        if det.as_f64() == 0.0 {
            return None;
        }

        let inv_00: E = a_ta[(1, 1)] / det;
        let inv_01: E = -a_ta[(0, 1)] / det;
        let inv_10: E = -a_ta[(1, 0)] / det;
        let inv_11: E = a_ta[(0, 0)] / det;
        let inv = Matrix2::new([[inv_00, inv_01], [inv_10, inv_11]]);

        let pinv: Matrix2x3<V> = inv * a_t;
        Some(pinv)
    }
}

impl<T, U, V> Mul<Matrix2<U>> for Matrix3x2<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity + Add<Output = V>,
{
    type Output = Matrix3x2<V>;

    fn mul(self, rhs: Matrix2<U>) -> Self::Output {
        let mut result = [[V::zero(); 2]; 3];
        for i in 0..3 {
            for j in 0..2 {
                result[i][j] = self[(i, 0)] * rhs[(0, j)] + self[(i, 1)] * rhs[(1, j)];
            }
        }
        Matrix3x2::new(result)
    }
}
