#[cfg(test)]
mod vector2_tests {
    pub fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
        (a - b).abs() < epsilon
    }
    use ndarray::arr1;
    use unitforge::small_linalg::Vector2;
    use unitforge::{Distance, DistanceUnit, Force, ForceUnit, PhysicsQuantity};

    #[test]
    fn test_add_assign_vector2() {
        let mut v1: Vector2<f64> = Vector2::from_f64([1.0, 2.0]);
        let v2 = Vector2::from_f64([3.0, 4.0]);
        v1 += v2;
        assert_eq!(v1, Vector2::from_f64([4.0, 6.0]));
    }

    #[test]
    fn test_sub_assign_vector2() {
        let mut v1 = Vector2::new([1.0, 2.0]);
        let v2 = Vector2::new([4.0, 5.0]);
        v1 -= v2;
        assert_eq!(v1.data(), [-3.0, -3.0]);
    }

    #[test]
    fn test_add_vector2() {
        let v1 = Vector2::new([1.0, 2.0]);
        let v2 = Vector2::new([3.0, 4.0]);
        let v3 = v1 + v2;
        assert_eq!(v3.data(), [4.0, 6.0]);
    }

    #[test]
    fn test_sub_vector2() {
        let v1 = Vector2::new([5.0, 7.0]);
        let v2 = Vector2::new([3.0, 4.0]);
        let v3 = v1 - v2;
        assert_eq!(v3.data(), [2.0, 3.0]);
    }

    #[test]
    fn test_vector2_from_ndarray() {
        let data = arr1(&[1.0, 2.0]);
        let v = Vector2::from_ndarray(data.view()).unwrap();
        assert_eq!(v.data(), [1.0, 2.0]);
    }

    #[test]
    fn test_vector2_to_ndarray() {
        let v = Vector2::new([2.0, 1.0]);
        let nd = v.to_ndarray();
        for i in 0..2 {
            assert!(approx_eq(nd[i], v[i], 1e-10));
        }
    }

    #[test]
    fn test_norm_of_zero_vector() {
        let v = Vector2::new([0.0, 0.0]);
        assert!((v.norm() - 0.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_unit_vectors() {
        let vx = Vector2::new([1.0, 0.0]);
        let vy = Vector2::new([0.0, 1.0]);
        assert!((vx.norm() - 1.0).abs() < f64::EPSILON);
        assert!((vy.norm() - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_arbitrary_vector() {
        let v = Vector2::new([3.0, 4.0]);
        assert!((v.norm() - 5.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_to_unit_vector() {
        let v = Vector2::new([
            Force::new(1.0, ForceUnit::N),
            Force::new(-2.0, ForceUnit::N),
        ]);
        let u = v.to_unit_vector();
        assert!((u.norm() - 1.0).abs() < f64::EPSILON);
        let collinearity = v.as_f64().dot_vct(&u) / v.norm().as_f64();
        assert!((collinearity - 1.0).abs() < f64::EPSILON);
    }

    #[test]
    fn test_quantity_times_vector2() {
        let f = Force::new(2.0, ForceUnit::kN);
        let v = Vector2::new([0.0, 1.0]);
        let f_v = v * f;
        assert_eq!(f_v[0], Force::new(0.0, ForceUnit::kN));
        assert_eq!(f_v[1], Force::new(2.0, ForceUnit::kN));
    }

    #[test]
    fn test_vector2_mul_assign() {
        let mut v = Vector2::new([1.0, 2.0]);
        v *= 2.0;
        assert_eq!(v.data(), [2.0, 4.0]);
    }

    #[test]
    fn test_vector2_div_assign() {
        let mut v = Vector2::new([4.0, 2.0]);
        v /= 2.0;
        assert_eq!(v.data(), [2.0, 1.0]);
    }

    #[test]
    fn test_vector2_mul_scalar() {
        let v: Vector2<f64> = Vector2::from_f64([1.0, 2.0]);
        let result = v * 2.0;
        assert_eq!(result.data(), [2.0, 4.0]);
    }

    #[test]
    fn test_vector2_div_scalar() {
        let v: Vector2<f64> = Vector2::from_f64([4.0, 6.0]);
        let result = v / 2.0;
        assert_eq!(result.data(), [2.0, 3.0]);
    }

    #[test]
    fn test_vector2_mul_vector2() {
        let a = Vector2::new([1.0, 2.0]);
        let b = Vector2::new([3.0, 4.0]);
        let result = a * b;
        assert_eq!(result.data(), [3.0, 8.0]);
    }

    #[test]
    fn test_vector2_mul_vector2_quantities() {
        let f: Vector2<f64> = Vector2::from_f64([2.0, 3.0]);
        let d = Vector2::new([
            Distance::new(2.0, DistanceUnit::m),
            Distance::new(4.0, DistanceUnit::m),
        ]);
        let result = f * d;
        let expected = Vector2::new([
            Distance::new(4.0, DistanceUnit::m),
            Distance::new(12.0, DistanceUnit::m),
        ]);
        assert!((result - expected).norm() < Distance::new(1E-10, DistanceUnit::m));
    }

    #[test]
    fn test_dot_product_vector2() {
        let f: Vector2<f64> = Vector2::from_f64([2.0, 3.0]);
        let d: Vector2<f64> = Vector2::from_f64([4.0, 5.0]);
        let dot = f.dot_vct(&d);
        assert_eq!(dot, 2.0 * 4.0 + 3.0 * 5.0);
    }

    #[test]
    fn test_vector2_times_zero_scalar() {
        let vector = Vector2::new([1.0, 2.0]);
        let scalar = 0.0;
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0]);
    }

    #[test]
    fn test_vector2_zero_scalar_times_vector2() {
        let scalar = 0.0;
        let vector = Vector2::new([1.0, 2.0]);
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0]);
    }

    #[test]
    fn test_norm_of_non_integer_values() {
        let v = Vector2::new([0.5, 0.5]);
        assert!((v.norm() - (0.5f64 * 0.5 + 0.5 * 0.5).sqrt()).abs() < f64::EPSILON);
    }

    #[test]
    fn test_abs() {
        let v = Vector2::new([-1.0, 2.0]);
        let abs = v.abs();
        assert_eq!(abs.data(), [1.0, 2.0]);
    }
}
