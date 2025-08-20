#[cfg(test)]
mod vector3_tests {
    pub fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
        (a - b).abs() < epsilon
    }

    use ndarray::arr1;
    use unitforge::small_linalg::Vector3;
    use unitforge::{
        Distance, DistanceUnit, Force, ForceDistance, ForceDistanceUnit, ForceUnit, PhysicsQuantity,
    };

    #[test]
    fn test_add_assign_vector3() {
        let mut v1: Vector3<Distance> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let v2 = Vector3::from_f64([4.0, 5.0, 6.0]);

        v1 += v2;
        assert_eq!(v1, Vector3::from_f64([5.0, 7.0, 9.0]));
    }

    #[test]
    fn test_sub_assign_vector3() {
        let mut v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        v1 -= v2;

        assert_eq!(v1.data(), [-3.0, -3.0, -3.0]);
    }

    #[test]
    fn test_add_vector3() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        let v3 = v1 + v2;

        assert_eq!(v3.data(), [5.0, 7.0, 9.0]);
    }

    #[test]
    fn test_sub_vector3() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 5.0, 6.0]);

        let v3 = v1 - v2;

        assert_eq!(v3.data(), [-3.0, -3.0, -3.0]);
    }

    #[test]
    fn test_vector3_from_ndarray() {
        let data = arr1(&[1., 2., 3.]);
        let v = Vector3::from_ndarray(data.view()).unwrap();
        for i in 0..3 {
            assert_eq!(v[i], data[i]);
        }
    }

    #[test]
    fn test_vector3_to_ndarray() {
        let v = Vector3::new([2.0, 1.0, 4.0]);
        let nd = v.to_ndarray();
        for i in 0..3 {
            assert!(approx_eq(nd[i], v[i], 1e-10));
        }
    }

    #[test]
    fn test_cross_product_basic() {
        let v1: Vector3<Force> = Vector3::from_f64([1.0, 0.0, 0.0]);
        let v2: Vector3<Distance> = Vector3::from_f64([0.0, 1.0, 0.0]);
        let cross_product: Vector3<ForceDistance> = v1.cross(&v2);
        assert_eq!(cross_product, Vector3::from_f64([0.0, 0.0, 1.0]));
    }

    #[test]
    fn test_cross_product_with_negative_values() {
        let v1 = Vector3::new([-1.0, 2.0, 3.0]);
        let v2 = Vector3::new([4.0, 0.0, -8.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [-16.0, 4.0, -8.0]);
    }

    #[test]
    fn test_cross_product_with_zero_vector() {
        let v1 = Vector3::new([0.0, 0.0, 0.0]);
        let v2 = Vector3::new([1.0, 2.0, 3.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_cross_product_of_parallel_vectors() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([2.0, 4.0, 6.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_cross_product_of_anti_parallel_vectors() {
        let v1 = Vector3::new([1.0, 2.0, 3.0]);
        let v2 = Vector3::new([-1.0, -2.0, -3.0]);
        let cross_product = v1.cross(&v2);
        assert_eq!(cross_product.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn test_norm_of_zero_vector() {
        let v = Vector3::new([0.0, 0.0, 0.0]);
        assert!((v.norm() - 0_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_unit_vectors() {
        let vx = Vector3::new([1.0, 0.0, 0.0]);
        let vy = Vector3::new([0.0, 1.0, 0.0]);
        let vz = Vector3::new([0.0, 0.0, 1.0]);

        assert!((vx.norm() - 1_f64).abs() < f64::EPSILON);
        assert!((vy.norm() - 1_f64).abs() < f64::EPSILON);
        assert!((vz.norm() - 1_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_arbitrary_vector() {
        let v = Vector3::new([3.0, 4.0, 0.0]);
        assert!((v.norm() - 5_f64).abs() < f64::EPSILON); // 3-4-5 right triangle
    }

    #[test]
    fn test_norm_of_negative_components() {
        let v = Vector3::new([-1.0, -2.0, -2.0]);
        assert!((v.norm() - 3_f64).abs() < f64::EPSILON); // sqrt(1 + 4 + 4) = 3
    }

    #[test]
    fn test_to_unit_vector() {
        let v = Vector3::new([
            Force::new(1.0, ForceUnit::N),
            Force::new(-2.0, ForceUnit::N),
            Force::new(-2.0, ForceUnit::N),
        ]);
        let u = v.to_unit_vector();
        assert!((u.norm() - 1.).abs().as_f64() < f64::EPSILON);
        let collinearity = v.as_f64().dot_vct(&u) / v.norm().as_f64();
        assert!((collinearity - 1_f64).abs() < f64::EPSILON);
    }

    #[test]
    fn test_quantity_times_vector() {
        let f = Force::new(1., ForceUnit::kN);
        let v = Vector3::new([0., 1., 0.]);
        let f_v = f * v;
        assert!((f_v[0] - Force::new(0., ForceUnit::kN)).as_f64().abs() < f64::EPSILON);
        assert!((f_v[1] - Force::new(1., ForceUnit::kN)).as_f64().abs() < f64::EPSILON);
        assert!((f_v[2] - Force::new(0., ForceUnit::kN)).as_f64().abs() < f64::EPSILON);
    }

    #[test]
    fn test_norm_of_non_integer_values() {
        let v = Vector3::new([0.5, 0.5, 0.5]);
        assert!((v.norm() - (0.75_f64).sqrt()).abs() < f64::EPSILON); // sqrt(0.25 + 0.25 + 0.25)
    }

    #[test]
    fn test_vector3_mul() {
        let v: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let result = v * 2.0;
        assert_eq!(
            result,
            Vector3::new([
                Force::new(2.0, ForceUnit::N),
                Force::new(4.0, ForceUnit::N),
                Force::new(6.0, ForceUnit::N)
            ])
        );
    }

    #[test]
    fn test_vector3_f64_mul_with_quantity() {
        let v: Vector3<f64> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let result = v * Distance::new(2.0, DistanceUnit::m);
        assert_eq!(
            result,
            Vector3::new([
                Distance::new(2.0, DistanceUnit::m),
                Distance::new(4.0, DistanceUnit::m),
                Distance::new(6.0, DistanceUnit::m)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_quantities() {
        let v: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let scalar = Distance::new(2., DistanceUnit::m);
        let result = v * scalar;
        assert_eq!(
            result,
            Vector3::new([
                ForceDistance::new(2.0, ForceDistanceUnit::Nm),
                ForceDistance::new(4.0, ForceDistanceUnit::Nm),
                ForceDistance::new(6.0, ForceDistanceUnit::Nm)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_vector3() {
        let a = Vector3::new([1., 2., 3.]);
        let b = Vector3::new([2., 4., 6.]);
        let result = a * b;
        assert_eq!(result, Vector3::new([2., 8., 18.]));
    }

    #[test]
    fn test_vector3_mul_vector3_quantities() {
        let forces: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);
        let distances = Vector3::new([
            Distance::new(2.0, DistanceUnit::m),
            Distance::new(3.0, DistanceUnit::m),
            Distance::new(4.0, DistanceUnit::m),
        ]);
        let result = forces * distances;
        let expected = Vector3::new([
            ForceDistance::new(2.0, ForceDistanceUnit::Nm),
            ForceDistance::new(6.0, ForceDistanceUnit::Nm),
            ForceDistance::new(12.0, ForceDistanceUnit::Nm),
        ]);
        assert!((result - expected).norm().as_f64() < 10E-10);
    }
    #[test]
    fn test_vector3_div() {
        let v: Vector3<Distance> = Vector3::from_f64([2.0, 4.0, 6.0]);
        let result = v / 2.0;
        assert_eq!(
            result,
            Vector3::new([
                Distance::new(1.0, DistanceUnit::m),
                Distance::new(2.0, DistanceUnit::m),
                Distance::new(3.0, DistanceUnit::m)
            ])
        );
    }

    #[test]
    fn test_vector3_mul_assign() {
        let mut v = Vector3::new([1.0, 2.0, 3.0]);
        v *= 2.0;
        assert_eq!(v, Vector3::new([2.0, 4.0, 6.0]));
    }

    #[test]
    fn test_vector3_div_assign() {
        let mut v = Vector3::new([2.0, 4.0, 6.0]);
        v /= 2.0;
        assert_eq!(v, Vector3::new([1.0, 2.0, 3.0]));
    }

    #[test]
    fn test_dot_vct_vector3() {
        let v1: Vector3<Force> = Vector3::from_f64([2.0, 4.0, 6.0]);
        let v2: Vector3<Distance> = Vector3::from_f64([1.0, 2.0, 3.0]);
        assert!(approx_eq(
            v1.dot_vct(&v2).to(ForceDistanceUnit::Nm),
            28.,
            1e-10
        ));
        assert!(approx_eq(
            v1.dot_vct(&v2).to(ForceDistanceUnit::Nm),
            28.,
            1e-10
        ));
    }

    #[test]
    fn vector3_times_scalar() {
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let scalar = 2.0;
        let result = vector * scalar;
        assert_eq!(result.data(), [2.0, 4.0, 6.0]);
    }

    #[test]
    fn scalar_times_vector3() {
        let scalar = 3.0;
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let result = vector * scalar;
        assert_eq!(result.data(), [3.0, 6.0, 9.0]);
    }

    #[test]
    fn vector3_times_zero_scalar() {
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let scalar = 0.0;
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn vector3_zero_scalar_times_vector3() {
        let scalar = 0.0;
        let vector = Vector3::new([1.0, 2.0, 3.0]);
        let result = vector * scalar;
        assert_eq!(result.data(), [0.0, 0.0, 0.0]);
    }

    #[test]
    fn vector3_abs() {
        let vector = Vector3::new([-1.0, 2.0, -3.0]);
        let result = vector.abs();
        assert_eq!(result.data(), [1.0, 2.0, 3.0]);
    }
}
