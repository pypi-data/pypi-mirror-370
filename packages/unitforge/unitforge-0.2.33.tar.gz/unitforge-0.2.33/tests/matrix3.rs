#[cfg(test)]
mod matrix3_tests {
    pub fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
        (a - b).abs() < epsilon
    }
    use unitforge::quantities::*;
    use unitforge::small_linalg::{Matrix3, Vector3};
    use unitforge::PhysicsQuantity;
    #[test]
    fn test_new() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix[(0, 0)], 1.0);
        assert_eq!(matrix[(2, 2)], 9.0);
    }

    #[test]
    fn test_zero() {
        let matrix: Matrix3<f64> = Matrix3::zero();
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(0, 1)], 0_f64);
        assert_eq!(matrix[(0, 2)], 0_f64);
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(1, 1)], 0_f64);
        assert_eq!(matrix[(2, 2)], 0_f64);
        assert_eq!(matrix[(0, 0)], 0_f64);
        assert_eq!(matrix[(1, 1)], 0_f64);
        assert_eq!(matrix[(2, 2)], 0_f64);
    }

    #[test]
    fn test_index() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix[(0, 0)], 1.0);
        assert_eq!(matrix[(1, 1)], 5.0);
        assert_eq!(matrix[(2, 2)], 9.0);
    }

    #[test]
    fn test_index_mut() {
        let mut matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        matrix[(0, 0)] = 10.0;
        matrix[(2, 2)] = 100.0;
        assert_eq!(matrix[(0, 0)], 10.0);
        assert_eq!(matrix[(2, 2)], 100.0);
    }

    #[test]
    fn test_det() {
        let matrix1 = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix1.det(), 0.0); // This matrix is singular, so determinant should be 0

        let matrix2 = Matrix3::new([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]);
        assert_eq!(matrix2.det(), 1.0); // Identity matrix, determinant should be 1

        let matrix3: Matrix3<Distance> =
            Matrix3::from_f64([[6.0, 1.0, 1.0], [4.0, -2.0, 5.0], [2.0, 8.0, 7.0]]);
        let deviation = (matrix3.det() - Volume::new(-306.0, VolumeUnit::mcb)).abs();
        assert!(deviation.get_power() < -10);
    }

    #[test]
    fn test_inverse() {
        let matrix1 = Matrix3::new([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]);
        let expected_inv1 =
            Matrix3::new([[-24.0, 18.0, 5.0], [20.0, -15.0, -4.0], [-5.0, 4.0, 1.0]]);
        assert_eq!(matrix1.inverse(), Some(expected_inv1));

        let matrix2 = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        assert_eq!(matrix2.inverse(), None); // This matrix is singular, so no inverse exists
    }

    #[test]
    fn test_inverse_distance() {
        let d = Distance::new(2., DistanceUnit::mm);
        let a = d * d;
        let v = d * d * d;
        let inverse_distance = a / v;
        assert!(approx_eq(
            inverse_distance.to(InverseDistanceUnit::_m),
            500.,
            10E-10
        ));

        let matrix1: Matrix3<Distance> =
            Matrix3::from_f64([[1.0, 2.0, 3.0], [0.0, 1.0, 4.0], [5.0, 6.0, 0.0]]);
        let expected_inv1: Matrix3<InverseDistance> =
            Matrix3::from_f64([[-24.0, 18.0, 5.0], [20.0, -15.0, -4.0], [-5.0, 4.0, 1.0]]);
        let inv = matrix1.inverse().unwrap();
        let diff = (expected_inv1 - inv).frobenius_norm();
        assert!(diff.get_power() < -12);
    }

    #[test]
    fn test_dot() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let vector = Vector3::new([1.0, 0.0, -1.0]);
        let result = matrix.dot(&vector);
        assert_eq!(result, Vector3::new([-2.0, -2.0, -2.0]));
    }

    #[test]
    fn test_add_matrix3() {
        let mat1 = Matrix3::new([[1_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        let result = mat1 + mat2;
        let expected = Matrix3::new([[3_f64; 3]; 3]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_sub_matrix3() {
        let mat1 = Matrix3::new([[3_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        let result = mat1 - mat2;
        let expected = Matrix3::new([[1_f64; 3]; 3]);
        assert_eq!(result, expected);
    }

    #[test]
    fn test_add_assign_matrix3() {
        let mut mat1 = Matrix3::new([[1_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        mat1 += mat2;
        let expected = Matrix3::new([[3_f64; 3]; 3]);
        assert_eq!(mat1, expected);
    }

    #[test]
    fn test_sub_assign_matrix3() {
        let mut mat1 = Matrix3::new([[3_f64; 3]; 3]);
        let mat2 = Matrix3::new([[2_f64; 3]; 3]);
        mat1 -= mat2;
        let expected = Matrix3::new([[1_f64; 3]; 3]);
        assert_eq!(mat1, expected);
    }

    #[test]
    fn test_transpose() {
        let matrix = Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]);
        let transposed = matrix.transpose();
        for i in 0..3 {
            for j in 0..3 {
                assert_eq!(matrix[(i, j)], transposed[(j, i)]);
            }
        }
    }

    #[test]
    fn test_abs() {
        let matrix = Matrix3::new([[-1.0, 2.0, -3.0], [4.0, -5.0, 6.0], [-7.0, 8.0, -9.0]]);
        let abs = matrix.abs();
        assert_eq!(
            abs,
            Matrix3::new([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        );
    }
}
