#[cfg(test)]
mod matrix2_tests {
    use unitforge::small_linalg::Matrix2;
    use unitforge::PhysicsQuantity;

    fn approx_eq(a: f64, b: f64, tol: f64) -> bool {
        (a - b).abs() < tol
    }

    #[test]
    fn test_matrix2_add() {
        let a: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let b = Matrix2::from_f64([[5.0, 6.0], [7.0, 8.0]]);
        let expected = Matrix2::from_f64([[6.0, 8.0], [10.0, 12.0]]);
        assert_eq!(a + b, expected);
    }

    #[test]
    fn test_matrix2_sub() {
        let a: Matrix2<f64> = Matrix2::from_f64([[5.0, 7.0], [9.0, 11.0]]);
        let b = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let expected = Matrix2::from_f64([[4.0, 5.0], [6.0, 7.0]]);
        assert_eq!(a - b, expected);
    }

    #[test]
    fn test_matrix2_add_assign() {
        let mut a: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let b = Matrix2::from_f64([[1.0, 1.0], [1.0, 1.0]]);
        a += b;
        assert_eq!(a, Matrix2::from_f64([[2.0, 3.0], [4.0, 5.0]]));
    }

    #[test]
    fn test_matrix2_sub_assign() {
        let mut a: Matrix2<f64> = Matrix2::from_f64([[5.0, 5.0], [5.0, 5.0]]);
        let b = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        a -= b;
        assert_eq!(a, Matrix2::from_f64([[4.0, 3.0], [2.0, 1.0]]));
    }

    #[test]
    fn test_matrix2_scalar_mul() {
        let m: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let result = m * 2.0;
        assert_eq!(result, Matrix2::from_f64([[2.0, 4.0], [6.0, 8.0]]));
    }

    #[test]
    fn test_matrix2_neg() {
        let m: Matrix2<f64> = Matrix2::from_f64([[1.0, -2.0], [-3.0, 4.0]]);
        let result = -m;
        assert_eq!(result, Matrix2::from_f64([[-1.0, 2.0], [3.0, -4.0]]));
    }

    #[test]
    fn test_matrix2_det() {
        let m: Matrix2<f64> = Matrix2::from_f64([[4.0, 3.0], [6.0, 3.0]]);
        let det = m.det();
        assert!(approx_eq(det.as_f64(), -6.0, 1e-10));
    }

    #[test]
    fn test_matrix2_inverse_exists() {
        let m: Matrix2<f64> = Matrix2::from_f64([[4.0, 7.0], [2.0, 6.0]]);
        let inv = m.inverse().unwrap();
        let expected = Matrix2::from_f64([[0.6, -0.7], [-0.2, 0.4]]);
        for i in 0..2 {
            for j in 0..2 {
                assert!(approx_eq(inv[(i, j)].as_f64(), expected[(i, j)], 1e-10));
            }
        }
    }

    #[test]
    fn test_matrix2_inverse_singular() {
        let m: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [2.0, 4.0]]);
        assert!(m.inverse().is_none());
    }

    #[test]
    fn test_matrix2_transpose() {
        let m: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let t = m.transpose();
        assert_eq!(t, Matrix2::from_f64([[1.0, 3.0], [2.0, 4.0]]));
    }

    #[test]
    fn test_matrix2_frobenius_norm() {
        let m: Matrix2<f64> = Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]);
        let norm = m.frobenius_norm().as_f64();
        assert!(approx_eq(norm, (1.0f64 + 4.0 + 9.0 + 16.0).sqrt(), 1e-10));
    }

    #[test]
    fn test_matrix2_abs() {
        let m: Matrix2<f64> = Matrix2::from_f64([[-1.0, 2.0], [-3.0, 4.0]]);
        let abs = m.abs();
        assert_eq!(abs, Matrix2::from_f64([[1.0, 2.0], [3.0, 4.0]]));
    }
}
