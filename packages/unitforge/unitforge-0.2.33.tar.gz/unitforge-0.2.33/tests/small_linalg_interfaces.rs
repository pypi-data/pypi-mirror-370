#[cfg(test)]
mod matrix2_vector2_tests {
    use unitforge::small_linalg::{Matrix2, Vector2};

    #[test]
    fn test_matrix2_dot_vector2() {
        let m: Matrix2<f64> = Matrix2::from_f64([[2.0, 0.0], [0.0, 3.0]]);
        let v: Vector2<f64> = Vector2::from_f64([1.0, 2.0]);
        let result = m.dot(&v);
        assert_eq!(result, Vector2::from_f64([2.0, 6.0]));
    }
    #[test]
    fn test_matrix2_get_row_col() {
        let m: Matrix2<f64> = Matrix2::from_f64([[10.0, 20.0], [30.0, 40.0]]);
        assert_eq!(m.get_row(0), Vector2::from_f64([10.0, 20.0]));
        assert_eq!(m.get_column(1), Vector2::from_f64([20.0, 40.0]));
    }
}

#[cfg(test)]
mod matrix2x3_dot_tests {
    use unitforge::small_linalg::{Matrix2x3, Vector2, Vector3};
    use unitforge::{Force, ForceUnit, PhysicsQuantity};

    #[test]
    fn test_dot_vector3_direct() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]);
        let v: Vector3<f64> = Vector3::from_f64([1.0, 1.0, 1.0]);
        let result = m.dot_vector3(&v);
        let expected = Vector2::from_f64([6.0, 15.0]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_mul_vector3_operator() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[2.0, 0.0, 1.0], [1.0, 3.0, 1.0]]);
        let v: Vector3<f64> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let result = m * v;
        let expected = Vector2::from_f64([5.0, 10.0]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_dot_vector3_with_units() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[2.0, 1.0, 0.0], [0.0, 1.0, 3.0]]);
        let v = Vector3::new([
            Force::new(1.0, ForceUnit::N),
            Force::new(2.0, ForceUnit::N),
            Force::new(3.0, ForceUnit::N),
        ]);
        let result = m.dot_vector3(&v);
        let expected = Vector2::new([
            Force::new(4.0, ForceUnit::N),
            Force::new(11.0, ForceUnit::N),
        ]);
        assert_eq!(result, expected);
    }
}

#[cfg(test)]
mod matrix3_vector3_tests {
    use unitforge::small_linalg::{Matrix3, Vector3};
    use unitforge::{Area, Distance, Force, ForceUnit, PhysicsQuantity};

    #[test]
    fn test_vector_element_times_matrix3() {
        let mat = Matrix3::new([[3_f64; 3]; 3]);
        let f = Force::new(1., ForceUnit::kN);
        let res = f * mat;
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(res[(i, j)], Force::new(3., ForceUnit::kN))
            }
        }
    }

    #[test]
    fn test_matrix3_times_vector_element() {
        let mat = Matrix3::new([[3_f64; 3]; 3]);
        let f = Force::new(1., ForceUnit::kN);
        let res = mat * f;
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(res[(i, j)], Force::new(3., ForceUnit::kN))
            }
        }
    }

    #[test]
    fn test_matrix3_dot() {
        let mat: Matrix3<Distance> = Matrix3::from_f64([[4., 7., 2.], [0., 3., 9.], [5., 1., 3.]]);
        let v: Vector3<Distance> = Vector3::from_f64([2., 6., 5.]);
        let res = mat.dot(&v);
        let expected: Vector3<Area> = Vector3::from_f64([60., 63., 31.]);
        assert!((res - expected).norm().as_f64() < f64::EPSILON);
    }

    #[test]
    fn test_solve() {
        let matrix = Matrix3::new([[2.0, -1.0, 0.0], [-1.0, 2.0, -1.0], [0.0, -1.0, 2.0]]);
        let rhs = Vector3::new([1.0, 0.0, 1.0]);
        let solution = matrix.solve(&rhs);

        assert!(solution.is_some());
        let sol = solution.unwrap();

        assert!((matrix.dot(&sol) - rhs)
            .data
            .iter()
            .all(|&x| x.abs() < 1e-6));
    }

    #[test]
    fn test_qr_decomposition() {
        let a = Matrix3::new([[12.0, -51.0, 4.0], [6.0, 167.0, -68.0], [-4.0, 24.0, -41.0]]);

        let (q, r) = a.qr_decomposition();

        let identity = q.transpose() * q;
        let expected_identity = Matrix3::identity();
        for i in 0..3 {
            for j in 0..3 {
                assert!((identity[(i, j)] - expected_identity[(i, j)]).abs() < 1e-6);
            }
        }
        let recomposed = q * r;
        for i in 0..3 {
            for j in 0..3 {
                assert!((recomposed[(i, j)] - a[(i, j)]).abs() < 1e-6);
            }
        }
    }

    #[test]
    fn test_qr_eigenvalues() {
        let a = Matrix3::new([[4.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 3.0]]);

        let eigen_pairs = a.qr_eigen(100, 1e-9);

        let expected_eigenvalues = [1.31260044, 2.56837289, 7.11902668];
        for (i, ev) in eigen_pairs.iter().enumerate() {
            assert!((ev.0 - expected_eigenvalues[i]).abs() < 1e-6);
        }
    }

    #[test]
    fn test_qr_eigenvectors() {
        let a = Matrix3::new([[4.0, -2.0, 1.0], [-2.0, 4.0, -2.0], [1.0, -2.0, 3.0]]);

        let eigen_pairs = a.qr_eigen(100, 1e-9);
        for i in 0..3 {
            let lambda = eigen_pairs[i].0;
            let v = eigen_pairs[i].1;
            let av = a.dot(&v);
            let expected = v * lambda;
            assert!((av - expected).norm() < 1e-6);
        }
    }

    #[test]
    fn test_get_column() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);

        assert_eq!(matrix.get_column(0).data, [1.0, 4.0, 7.0]);
        assert_eq!(matrix.get_column(1).data, [2.0, 5.0, 8.0]);
        assert_eq!(matrix.get_column(2).data, [3.0, 6.0, 9.0]);
    }

    #[test]
    fn test_set_column() {
        let mut matrix = Matrix3::zero();
        let column = Vector3::new([1.0, 2.0, 3.0]);
        matrix.set_column(1, column);

        assert_eq!(matrix[(0, 1)], 1.0);
        assert_eq!(matrix[(1, 1)], 2.0);
        assert_eq!(matrix[(2, 1)], 3.0);
    }

    #[test]
    fn test_get_row() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);

        assert_eq!(matrix.get_row(0), Vector3::new([1.0, 2.0, 3.0]));
        assert_eq!(matrix.get_row(1), Vector3::new([4.0, 5.0, 6.0]));
        assert_eq!(matrix.get_row(2), Vector3::new([7.0, 8.0, 9.0]));
    }

    #[test]
    fn test_set_row() {
        let mut matrix = Matrix3::zero();
        let row = Vector3::new([1.0, 2.0, 3.0]);
        matrix.set_row(1, row);

        assert_eq!(matrix[(1, 0)], 1.0);
        assert_eq!(matrix[(1, 1)], 2.0);
        assert_eq!(matrix[(1, 2)], 3.0);
    }

    #[test]
    fn test_from_rows() {
        let rows = [
            Vector3::new([1.0, 2.0, 3.0]),
            Vector3::new([4.0, 5.0, 6.0]),
            Vector3::new([7.0, 8.0, 9.0]),
        ];
        let matrix = Matrix3::from_rows(&rows);
        for i in 0..3 {
            assert!((matrix.get_row(i) - rows[i]).norm() < 1E-10);
        }
    }

    #[test]
    fn test_from_columns() {
        let columns = [
            Vector3::new([1.0, 4.0, 7.0]),
            Vector3::new([2.0, 5.0, 8.0]),
            Vector3::new([3.0, 6.0, 9.0]),
        ];
        let matrix = Matrix3::from_columns(&columns);
        for i in 0..3 {
            assert!((matrix.get_column(i) - columns[i]).norm() < 1E-10);
        }
    }

    #[test]
    fn test_matrix_multiplication() {
        let a = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let b = Matrix3::new([[9.0, 8.0, 7.0], [6.0, 5.0, 4.0], [3.0, 2.0, 1.0]]);
        let result = a * b;
        let expected = Matrix3::new([[30.0, 24.0, 18.0], [84.0, 69.0, 54.0], [138.0, 114.0, 90.0]]);
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(result[(i, j)], expected[(i, j)]);
            }
        }
    }
}

#[cfg(test)]
mod matrix3x2_dot_tests {
    use unitforge::small_linalg::{Matrix3x2, Vector2, Vector3};
    use unitforge::{Distance, DistanceUnit, PhysicsQuantity};

    #[test]
    fn test_dot_vector2_direct() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let v: Vector2<f64> = Vector2::from_f64([1.0, 1.0]);
        let result = m.dot_vector2(&v);
        let expected = Vector3::from_f64([3.0, 7.0, 11.0]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_mul_vector2_operator() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 0.0], [0.0, 1.0], [2.0, 2.0]]);
        let v: Vector2<f64> = Vector2::from_f64([2.0, 3.0]);
        let result = m * v;
        let expected = Vector3::from_f64([2.0, 3.0, 10.0]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_dot_vector2_with_units() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [0.0, 1.0], [3.0, 0.0]]);
        let v = Vector2::new([
            Distance::new(2.0, DistanceUnit::m),
            Distance::new(1.0, DistanceUnit::m),
        ]);
        let result = m.dot_vector2(&v);
        let expected = Vector3::new([
            Distance::new(4.0, DistanceUnit::m),
            Distance::new(1.0, DistanceUnit::m),
            Distance::new(6.0, DistanceUnit::m),
        ]);
        assert_eq!(result, expected);
    }
}

#[cfg(test)]
mod matrix3_mul_matrix3x2_tests {
    use unitforge::small_linalg::{Matrix3, Matrix3x2};

    #[test]
    fn test_matrix3_times_matrix3x2() {
        let a: Matrix3<f64> =
            Matrix3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]);
        let b: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [0.0, 1.0], [4.0, 0.0]]);

        let result = a * b;
        let expected = Matrix3x2::from_f64([[13.0, 4.0], [16.0, 1.0], [5.0, 16.0]]);

        assert_eq!(result, expected);
    }
}

#[cfg(test)]
mod matrix2_mul_matrix2x3_tests {
    use unitforge::small_linalg::{Matrix2, Matrix2x3};

    #[test]
    fn test_matrix2_times_matrix2x3() {
        let a: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let b: Matrix2x3<f64> = Matrix2x3::from_f64([[2.0, 0.0, 1.0], [1.0, 2.0, 3.0]]);

        let result = a * b;
        let expected = Matrix2x3::from_f64([[4.0, 4.0, 7.0], [10.0, 8.0, 15.0]]);

        assert_eq!(result, expected);
    }
}

#[cfg(test)]
mod matrix3x2_mul_matrix2x3_tests {
    use unitforge::small_linalg::{Matrix2x3, Matrix3, Matrix3x2};

    #[test]
    fn test_matrix3x2_times_matrix2x3() {
        let a: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let b: Matrix2x3<f64> = Matrix2x3::from_f64([[7.0, 8.0, 9.0], [0.0, 1.0, 2.0]]);

        let result = a * b;
        let expected =
            Matrix3::from_f64([[7.0, 10.0, 13.0], [21.0, 28.0, 35.0], [35.0, 46.0, 57.0]]);

        assert_eq!(result, expected);
    }
}

#[cfg(test)]
mod matrix2x3_mul_matrix3x2_tests {
    use unitforge::small_linalg::{Matrix2, Matrix2x3, Matrix3x2};

    #[test]
    fn test_matrix2x3_times_matrix3x2() {
        let a: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]);
        let b: Matrix3x2<f64> = Matrix3x2::from_f64([[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]]);

        let result = a * b;
        let expected = Matrix2::from_f64([[58.0, 64.0], [139.0, 154.0]]);

        assert_eq!(result, expected);
    }
}
