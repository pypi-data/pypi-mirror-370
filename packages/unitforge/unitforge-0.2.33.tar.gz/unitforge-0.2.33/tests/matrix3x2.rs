#[cfg(test)]
mod matrix3x2_tests {
    use unitforge::small_linalg::{Matrix2x3, Matrix3x2};
    use unitforge::{
        Distance, DistanceUnit, Force, ForceUnit, InverseDistanceUnit, PhysicsQuantity,
    };

    #[test]
    fn test_creation_and_indexing() {
        let m: Matrix3x2<Force> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        assert_eq!(m[(0, 1)], Force::new(2.0, ForceUnit::N));
        assert_eq!(m[(2, 0)], Force::new(5.0, ForceUnit::N));
    }

    #[test]
    fn test_zero() {
        let m: Matrix3x2<f64> = Matrix3x2::zero();
        for i in 0..3 {
            for j in 0..2 {
                assert_eq!(m[(i, j)], 0.0);
            }
        }
    }

    #[test]
    fn test_addition() {
        let a: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]);
        let b = Matrix3x2::from_f64([[2.0, 2.0], [2.0, 2.0], [2.0, 2.0]]);
        let expected = Matrix3x2::from_f64([[3.0, 3.0], [3.0, 3.0], [3.0, 3.0]]);
        assert_eq!(a + b, expected);
    }

    #[test]
    fn test_subtraction() {
        let a: Matrix3x2<f64> = Matrix3x2::from_f64([[4.0, 4.0], [4.0, 4.0], [4.0, 4.0]]);
        let b = Matrix3x2::from_f64([[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]);
        let expected = Matrix3x2::from_f64([[3.0, 3.0], [3.0, 3.0], [3.0, 3.0]]);
        assert_eq!(a - b, expected);
    }

    #[test]
    fn test_negation() {
        let a: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, -2.0], [3.0, -4.0], [5.0, -6.0]]);
        let expected = Matrix3x2::from_f64([[-1.0, 2.0], [-3.0, 4.0], [-5.0, 6.0]]);
        assert_eq!(-a, expected);
    }

    #[test]
    fn test_transpose() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let trans = m.transpose();
        let expected = Matrix2x3::from_f64([[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]]);
        assert_eq!(trans, expected);
    }

    #[test]
    fn test_row() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let row = m.row(1);
        assert_eq!(row[0], m[(1, 0)]);
        assert_eq!(row[1], m[(1, 1)]);
    }

    #[test]
    fn test_column() {
        let m: Matrix3x2<f64> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let column = m.column(1);
        assert_eq!(column[0], m[(0, 1)]);
        assert_eq!(column[1], m[(1, 1)]);
        assert_eq!(column[2], m[(2, 1)]);
    }

    #[test]
    fn test_pseudoinverse_matrix3x2() {
        let a: Matrix3x2<Distance> = Matrix3x2::from_f64([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]);
        let pinv = a.pseudoinverse().unwrap();

        let triple = (a * pinv) * a;
        let diff = triple - a;
        for i in 0..3 {
            for j in 0..2 {
                assert!(diff[(i, j)].abs() < Distance::new(1E-10, DistanceUnit::m));
            }
        }

        let pinv_triple = (pinv * a) * pinv;
        let diff = pinv_triple - pinv;
        for i in 0..2 {
            for j in 0..3 {
                assert!(diff[(i, j)].abs().to(InverseDistanceUnit::_mm) < 1E-10);
            }
        }
    }

    #[test]
    fn test_abs() {
        let matrix = Matrix3x2::new([[-1.0, 2.0], [-3.0, 4.0], [-5.0, 6.0]]);
        let abs = matrix.abs();
        assert_eq!(abs, Matrix3x2::new([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]));
    }
}
