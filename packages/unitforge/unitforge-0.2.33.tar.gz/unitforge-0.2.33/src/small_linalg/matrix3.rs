use crate::{small_linalg::Vector3, PhysicsQuantity};
use std::ops::{Add, AddAssign, Div, Index, IndexMut, Mul, Neg, Sub, SubAssign};

#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Matrix3<T: PhysicsQuantity> {
    data: [[T; 3]; 3],
}

impl<T> Neg for Matrix3<T>
where
    T: PhysicsQuantity + Neg<Output = T>,
{
    type Output = Self;

    fn neg(self) -> Self::Output {
        Matrix3 {
            data: [
                [
                    self.data[0][0].neg(),
                    self.data[0][1].neg(),
                    self.data[0][2].neg(),
                ],
                [
                    self.data[1][0].neg(),
                    self.data[1][1].neg(),
                    self.data[1][2].neg(),
                ],
                [
                    self.data[2][0].neg(),
                    self.data[2][1].neg(),
                    self.data[2][2].neg(),
                ],
            ],
        }
    }
}

impl<T: PhysicsQuantity> Add for Matrix3<T> {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        Self {
            data: [
                [
                    self.data[0][0] + other.data[0][0],
                    self.data[0][1] + other.data[0][1],
                    self.data[0][2] + other.data[0][2],
                ],
                [
                    self.data[1][0] + other.data[1][0],
                    self.data[1][1] + other.data[1][1],
                    self.data[1][2] + other.data[1][2],
                ],
                [
                    self.data[2][0] + other.data[2][0],
                    self.data[2][1] + other.data[2][1],
                    self.data[2][2] + other.data[2][2],
                ],
            ],
        }
    }
}

impl<T: PhysicsQuantity> Sub for Matrix3<T> {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        Self {
            data: [
                [
                    self.data[0][0] - other.data[0][0],
                    self.data[0][1] - other.data[0][1],
                    self.data[0][2] - other.data[0][2],
                ],
                [
                    self.data[1][0] - other.data[1][0],
                    self.data[1][1] - other.data[1][1],
                    self.data[1][2] - other.data[1][2],
                ],
                [
                    self.data[2][0] - other.data[2][0],
                    self.data[2][1] - other.data[2][1],
                    self.data[2][2] - other.data[2][2],
                ],
            ],
        }
    }
}

impl<T: PhysicsQuantity> AddAssign for Matrix3<T> {
    fn add_assign(&mut self, other: Self) {
        self.data[0][0] += other.data[0][0];
        self.data[0][1] += other.data[0][1];
        self.data[0][2] += other.data[0][2];

        self.data[1][0] += other.data[1][0];
        self.data[1][1] += other.data[1][1];
        self.data[1][2] += other.data[1][2];

        self.data[2][0] += other.data[2][0];
        self.data[2][1] += other.data[2][1];
        self.data[2][2] += other.data[2][2];
    }
}

impl<T: PhysicsQuantity> SubAssign for Matrix3<T> {
    fn sub_assign(&mut self, other: Self) {
        self.data[0][0] -= other.data[0][0];
        self.data[0][1] -= other.data[0][1];
        self.data[0][2] -= other.data[0][2];

        self.data[1][0] -= other.data[1][0];
        self.data[1][1] -= other.data[1][1];
        self.data[1][2] -= other.data[1][2];

        self.data[2][0] -= other.data[2][0];
        self.data[2][1] -= other.data[2][1];
        self.data[2][2] -= other.data[2][2];
    }
}

impl<T, U, V> Mul<U> for Matrix3<T>
where
    T: PhysicsQuantity + Mul<U, Output = V>,
    U: PhysicsQuantity,
    V: PhysicsQuantity,
{
    type Output = Matrix3<V>;

    fn mul(self, scalar: U) -> Matrix3<V> {
        Matrix3 {
            data: [
                [
                    self.data[0][0] * scalar,
                    self.data[0][1] * scalar,
                    self.data[0][2] * scalar,
                ],
                [
                    self.data[1][0] * scalar,
                    self.data[1][1] * scalar,
                    self.data[1][2] * scalar,
                ],
                [
                    self.data[2][0] * scalar,
                    self.data[2][1] * scalar,
                    self.data[2][2] * scalar,
                ],
            ],
        }
    }
}

impl<T: PhysicsQuantity> Matrix3<T> {
    pub fn new(data: [[T; 3]; 3]) -> Self {
        Self { data }
    }

    pub fn zero() -> Self {
        Self {
            data: [[T::zero(); 3]; 3],
        }
    }

    pub fn from_f64(data: [[f64; 3]; 3]) -> Self {
        let mut quantity_data = [[T::zero(); 3]; 3];
        quantity_data[0][0] = T::from_raw(data[0][0]);
        quantity_data[0][1] = T::from_raw(data[0][1]);
        quantity_data[0][2] = T::from_raw(data[0][2]);

        quantity_data[1][0] = T::from_raw(data[1][0]);
        quantity_data[1][1] = T::from_raw(data[1][1]);
        quantity_data[1][2] = T::from_raw(data[1][2]);

        quantity_data[2][0] = T::from_raw(data[2][0]);
        quantity_data[2][1] = T::from_raw(data[2][1]);
        quantity_data[2][2] = T::from_raw(data[2][2]);
        Self::new(quantity_data)
    }

    pub fn data(&self) -> [[T; 3]; 3] {
        self.data
    }

    #[deprecated(since = "0.2.9", note = "please use `as_f64()` instead")]
    pub fn to_raw(&self) -> Matrix3<f64> {
        self.as_f64()
    }

    pub fn as_f64(&self) -> Matrix3<f64> {
        Matrix3::new([
            [
                self.data()[0][0].as_f64(),
                self.data()[0][1].as_f64(),
                self.data()[0][2].as_f64(),
            ],
            [
                self.data()[1][0].as_f64(),
                self.data()[1][1].as_f64(),
                self.data()[1][2].as_f64(),
            ],
            [
                self.data()[2][0].as_f64(),
                self.data()[2][1].as_f64(),
                self.data()[2][2].as_f64(),
            ],
        ])
    }

    #[deprecated(since = "0.2.9", note = "please use `from` instead")]
    pub fn from_raw(raw: Matrix3<f64>) -> Self {
        Self {
            data: [
                [
                    T::from_raw(raw[(0, 0)]),
                    T::from_raw(raw[(0, 1)]),
                    T::from_raw(raw[(0, 2)]),
                ],
                [
                    T::from_raw(raw[(1, 0)]),
                    T::from_raw(raw[(1, 1)]),
                    T::from_raw(raw[(1, 2)]),
                ],
                [
                    T::from_raw(raw[(2, 0)]),
                    T::from_raw(raw[(2, 1)]),
                    T::from_raw(raw[(2, 2)]),
                ],
            ],
        }
    }

    pub fn from_rows(rows: &[Vector3<T>; 3]) -> Self {
        Self {
            data: [
                [rows[0][0], rows[0][1], rows[0][2]],
                [rows[1][0], rows[1][1], rows[1][2]],
                [rows[2][0], rows[2][1], rows[2][2]],
            ],
        }
    }

    pub fn from_columns(columns: &[Vector3<T>; 3]) -> Self {
        Self::from_rows(columns).transpose()
    }

    pub fn get_column(&self, col: usize) -> Vector3<T> {
        assert!(col < 3, "Column index out of bounds");
        Vector3::new([self.data[0][col], self.data[1][col], self.data[2][col]])
    }

    pub fn set_column(&mut self, col: usize, vec: Vector3<T>) {
        for i in 0..3 {
            self[(i, col)] = vec[i];
        }
    }

    pub fn get_row(&self, row: usize) -> Vector3<T> {
        assert!(row < 3, "Row index out of bounds");
        Vector3::new(self.data[row])
    }

    pub fn set_row(&mut self, row: usize, vec: Vector3<T>) {
        for i in 0..3 {
            self[(row, i)] = vec[i];
        }
    }

    pub fn transpose(&self) -> Matrix3<T> {
        let mut res = Self::zero();
        for i in 0..3 {
            for j in 0..3 {
                res[(i, j)] = self[(j, i)];
            }
        }
        res
    }

    pub fn frobenius_norm(&self) -> T {
        let mut acc = 0.;
        for i in 0..3 {
            for j in 0..3 {
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
                [
                    self.data[0][0].abs(),
                    self.data[0][1].abs(),
                    self.data[0][2].abs(),
                ],
                [
                    self.data[1][0].abs(),
                    self.data[1][1].abs(),
                    self.data[1][2].abs(),
                ],
                [
                    self.data[2][0].abs(),
                    self.data[2][1].abs(),
                    self.data[2][2].abs(),
                ],
            ],
        }
    }
}

impl<T: PhysicsQuantity> Matrix3<T> {
    #[inline(always)]
    pub fn dot<U, V>(&self, vec: &Vector3<U>) -> Vector3<V>
    where
        T: Mul<U, Output = V>,
        U: PhysicsQuantity,
        V: PhysicsQuantity + Add<Output = V>,
    {
        let result = [
            self.data[0][0] * vec.data[0]
                + self.data[0][1] * vec.data[1]
                + self.data[0][2] * vec.data[2],
            self.data[1][0] * vec.data[0]
                + self.data[1][1] * vec.data[1]
                + self.data[1][2] * vec.data[2],
            self.data[2][0] * vec.data[0]
                + self.data[2][1] * vec.data[1]
                + self.data[2][2] * vec.data[2],
        ];
        Vector3::new(result)
    }
}

impl<T, U, V: PhysicsQuantity> Matrix3<T>
where
    T: PhysicsQuantity + Mul<Output = U> + Mul<U, Output = V>,
    U: Add<Output = U> + Sub<Output = U> + Mul<T, Output = V>,
{
    #[inline(always)]
    pub fn det(&self) -> V {
        let a = self[(0, 0)];
        let b = self[(0, 1)];
        let c = self[(0, 2)];
        let d = self[(1, 0)];
        let e = self[(1, 1)];
        let f = self[(1, 2)];
        let g = self[(2, 0)];
        let h = self[(2, 1)];
        let i = self[(2, 2)];
        a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    }
}

impl<T, U, V, R> Matrix3<T>
where
    T: PhysicsQuantity + Mul<T, Output = U> + Mul<U, Output = V>,
    U: PhysicsQuantity + Mul<T, Output = V>,
    U: PhysicsQuantity + Div<V, Output = R>,
    V: PhysicsQuantity,
    R: PhysicsQuantity,
{
    pub fn inverse(&self) -> Option<Matrix3<R>> {
        let det = self.det(); // det is of type V

        let a = self[(0, 0)];
        let b = self[(0, 1)];
        let c = self[(0, 2)];
        let d = self[(1, 0)];
        let e = self[(1, 1)];
        let f = self[(1, 2)];
        let g = self[(2, 0)];
        let h = self[(2, 1)];
        let i = self[(2, 2)];

        let inv = [
            [
                ((e * i) - (f * h)) / det,
                -((b * i) - (c * h)) / det,
                ((b * f) - (c * e)) / det,
            ],
            [
                -((d * i) - (f * g)) / det,
                ((a * i) - (c * g)) / det,
                -((a * f) - (c * d)) / det,
            ],
            [
                ((d * h) - (e * g)) / det,
                -((a * h) - (b * g)) / det,
                ((a * e) - (b * d)) / det,
            ],
        ];

        if (inv[0][0]
            + inv[0][1]
            + inv[0][2]
            + inv[1][0]
            + inv[1][1]
            + inv[1][2]
            + inv[2][0]
            + inv[2][1]
            + inv[2][2])
            .as_f64()
            .is_nan()
        {
            None
        } else {
            Some(Matrix3::new(inv))
        }
    }
}

impl<T: PhysicsQuantity> Index<(usize, usize)> for Matrix3<T> {
    type Output = T;

    fn index(&self, index: (usize, usize)) -> &T {
        &self.data[index.0][index.1]
    }
}

impl<T: PhysicsQuantity> IndexMut<(usize, usize)> for Matrix3<T> {
    fn index_mut(&mut self, index: (usize, usize)) -> &mut T {
        &mut self.data[index.0][index.1]
    }
}

impl<T> Matrix3<T>
where
    T: PhysicsQuantity
        + Mul<T, Output = T>
        + Add<T, Output = T>
        + Sub<T, Output = T>
        + Div<T, Output = T>,
{
    pub fn solve(&self, rhs: &Vector3<T>) -> Option<Vector3<T>> {
        self.inverse().map(|inverse| inverse.dot(rhs))
    }
}

impl Mul for Matrix3<f64> {
    type Output = Matrix3<f64>;

    fn mul(self, other: Matrix3<f64>) -> Matrix3<f64> {
        let mut result = Matrix3::zero();

        for i in 0..3 {
            for j in 0..3 {
                result[(i, j)] = self[(i, 0)] * other[(0, j)]
                    + self[(i, 1)] * other[(1, j)]
                    + self[(i, 2)] * other[(2, j)];
            }
        }

        result
    }
}

impl Matrix3<f64> {
    pub fn qr_eigen(&self, max_iterations: usize, tol: f64) -> Vec<(f64, Vector3<f64>)> {
        let mut a_k = *self;
        let mut q_total = Matrix3::identity();

        for _ in 0..max_iterations {
            let (q, r) = a_k.qr_decomposition();
            a_k = r * q;
            q_total = q_total * q;

            if a_k.off_diagonal_norm() < tol {
                break;
            }
        }

        let eigenvalues = Vector3::new([a_k[(0, 0)], a_k[(1, 1)], a_k[(2, 2)]]);

        let mut eigen_pairs = vec![
            (eigenvalues[0], q_total.get_column(0)),
            (eigenvalues[1], q_total.get_column(1)),
            (eigenvalues[2], q_total.get_column(2)),
        ];
        eigen_pairs.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        eigen_pairs
    }

    pub fn qr_decomposition(&self) -> (Matrix3<f64>, Matrix3<f64>) {
        let mut q = Matrix3::identity();
        let mut r = Matrix3::zero();

        let mut a_cols = [
            Vector3::new([self[(0, 0)], self[(1, 0)], self[(2, 0)]]),
            Vector3::new([self[(0, 1)], self[(1, 1)], self[(2, 1)]]),
            Vector3::new([self[(0, 2)], self[(1, 2)], self[(2, 2)]]),
        ];

        for i in 0..3 {
            r[(i, i)] = a_cols[i].norm();
            q.set_column(i, a_cols[i] / r[(i, i)]);

            for j in (i + 1)..3 {
                r[(i, j)] = q.get_column(i).dot_vct(&a_cols[j]);
                a_cols[j] -= q.get_column(i) * r[(i, j)];
            }
        }

        (q, r)
    }

    fn off_diagonal_norm(&self) -> f64 {
        let mut sum = 0.0;
        for i in 0..3 {
            for j in 0..3 {
                if i != j {
                    sum += self[(i, j)].powi(2);
                }
            }
        }
        sum.sqrt()
    }

    pub fn identity() -> Self {
        Matrix3::new([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    }
}
