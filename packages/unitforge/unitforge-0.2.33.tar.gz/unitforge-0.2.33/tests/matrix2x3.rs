#[cfg(test)]
mod matrix2x3_tests {
    use unitforge::small_linalg::{Matrix2x3, Matrix3x2};
    use unitforge::{Distance, DistanceUnit, InverseDistanceUnit, PhysicsQuantity};

    #[test]
    fn test_creation_and_indexing() {
        let m: Matrix2x3<Distance> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]);
        assert_eq!(m[(0, 0)], Distance::new(1.0, DistanceUnit::m));
        assert_eq!(m[(1, 2)], Distance::new(6.0, DistanceUnit::m));
    }

    #[test]
    fn test_zero() {
        let m: Matrix2x3<f64> = Matrix2x3::zero();
        for i in 0..2 {
            for j in 0..3 {
                assert_eq!(m[(i, j)], 0.0);
            }
        }
    }

    #[test]
    fn test_addition() {
        let a: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]);
        let b = Matrix2x3::from_f64([[6.0, 5.0, 4.0], [3.0, 2.0, 1.0]]);
        let expected = Matrix2x3::from_f64([[7.0, 7.0, 7.0], [7.0, 7.0, 7.0]]);
        assert_eq!(a + b, expected);
    }

    #[test]
    fn test_subtraction() {
        let a: Matrix2x3<f64> = Matrix2x3::from_f64([[6.0, 5.0, 4.0], [3.0, 2.0, 1.0]]);
        let b = Matrix2x3::from_f64([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]);
        let expected = Matrix2x3::from_f64([[5.0, 4.0, 3.0], [2.0, 1.0, 0.0]]);
        assert_eq!(a - b, expected);
    }

    #[test]
    fn test_negation() {
        let a: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, -2.0, 3.0], [-4.0, 5.0, -6.0]]);
        let expected = Matrix2x3::from_f64([[-1.0, 2.0, -3.0], [4.0, -5.0, 6.0]]);
        assert_eq!(-a, expected);
    }

    #[test]
    fn test_transpose() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]);
        let trans = m.transpose();
        let expected = Matrix3x2::from_f64([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]]);
        assert_eq!(trans, expected);
    }

    #[test]
    fn test_pseudoinverse_matrix2x3() {
        let a: Matrix2x3<Distance> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0]]);
        let pinv = a.pseudoinverse().unwrap();

        let triple = (a * pinv) * a;
        let diff = triple - a;
        for i in 0..2 {
            for j in 0..3 {
                assert!(diff[(i, j)].abs().to(DistanceUnit::mm) < 1E-10);
            }
        }

        let pinv_triple = (pinv * a) * pinv;

        let diff = pinv_triple - pinv;
        for i in 0..3 {
            for j in 0..2 {
                assert!(diff[(i, j)].abs().to(InverseDistanceUnit::_m) < 1E-10);
            }
        }
    }

    #[test]
    fn test_row() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0]]);
        let row = m.row(1);
        assert_eq!(row[0], m[(1, 0)]);
        assert_eq!(row[1], m[(1, 1)]);
        assert_eq!(row[2], m[(1, 2)]);
    }

    #[test]
    fn test_column() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0]]);
        let column = m.column(1);
        assert_eq!(column[0], m[(0, 1)]);
        assert_eq!(column[1], m[(1, 1)]);
    }

    #[test]
    fn test_abs() {
        let m: Matrix2x3<f64> = Matrix2x3::from_f64([[-1.0, 2.0, -3.0], [4.0, -5.0, 6.0]]);
        let abs = m.abs();
        assert_eq!(abs, Matrix2x3::from_f64([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]));
    }
}
