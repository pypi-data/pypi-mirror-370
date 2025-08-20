pub fn approx_eq(a: f64, b: f64, epsilon: f64) -> bool {
    (a - b).abs() < epsilon
}

#[cfg(test)]
mod test_force {
    use ndarray::{arr1, arr2};
    use num_traits::Zero;
    use unitforge::prelude::*;
    use unitforge::quantities::Force;
    use unitforge::quantities::ForceUnit;
    use unitforge::{Distance, DistanceUnit};

    #[test]
    fn test_force_creation() {
        let f = Force::new(100.0, ForceUnit::kN);
        assert_eq!(f.to(ForceUnit::N), 100_000.0);
    }

    #[test]
    fn test_is_not_nan() {
        let f = Force::new(100.0, ForceUnit::kN);
        assert!(!f.is_nan());
    }

    #[test]
    fn test_is_nan() {
        let f = Force::new(f64::NAN, ForceUnit::kN);
        assert!(f.is_nan());
    }

    #[test]
    fn test_distance_weird() {
        let f = Distance::new(100.0, DistanceUnit::m);
        assert_eq!(f.to(DistanceUnit::AU), 6.684587122268447e-10);
    }
    #[test]
    fn test_force_addition() {
        let f1 = Force::new(50.0, ForceUnit::kN);
        let f2 = Force::new(50.0, ForceUnit::kN);
        let f3 = f1 + f2;
        assert_eq!(f3.to(ForceUnit::kN), 100.0);
    }

    #[test]
    fn test_force_subtraction() {
        let f1 = Force::new(80.0, ForceUnit::kN);
        let f2 = Force::new(30.0, ForceUnit::kN);
        let f3 = f1 - f2;
        assert_eq!(f3.to(ForceUnit::kN), 50.0);
    }

    #[test]
    fn test_min() {
        let f1 = Force::new(80.0, ForceUnit::kN);
        let f2 = Force::new(30.0, ForceUnit::kN);
        let f3 = f1.min(f2);
        assert_eq!(f3.to(ForceUnit::kN), 30.0);
    }

    #[test]
    fn test_max() {
        let f1 = Force::new(80.0, ForceUnit::kN);
        let f2 = Force::new(30.0, ForceUnit::kN);
        let f3 = f1.max(f2);
        assert_eq!(f3.to(ForceUnit::kN), 80.0);
    }

    #[test]
    fn test_force_addition_arr1() {
        let f1 = arr1(&[
            Force::new(50.0, ForceUnit::kN),
            Force::new(75.0, ForceUnit::kN),
        ]);
        let f2 = arr1(&[
            Force::new(25.0, ForceUnit::kN),
            Force::new(15.0, ForceUnit::kN),
        ]);
        let f3 = f1 + f2;
        assert_eq!(f3[0].to(ForceUnit::kN), 75.0);
        assert_eq!(f3[1].to(ForceUnit::kN), 90.0);
    }

    #[test]
    fn test_force_addition_arr2() {
        let f1 = arr2(&[[
            Force::new(50.0, ForceUnit::kN),
            Force::new(75.0, ForceUnit::kN),
        ]]);
        let f2 = arr2(&[[
            Force::new(25.0, ForceUnit::kN),
            Force::new(15.0, ForceUnit::kN),
        ]]);
        let f3 = f1 + f2;
        assert_eq!(f3[[0, 0]].to(ForceUnit::kN), 75.0);
        assert_eq!(f3[[0, 1]].to(ForceUnit::kN), 90.0);
    }

    #[test]
    fn test_force_subtraction_arr1() {
        let f1 = arr1(&[
            Force::new(50.0, ForceUnit::kN),
            Force::new(75.0, ForceUnit::kN),
        ]);
        let f2 = arr1(&[
            Force::new(25.0, ForceUnit::kN),
            Force::new(15.0, ForceUnit::kN),
        ]);
        let f3 = f1 - f2;
        assert_eq!(f3[0].to(ForceUnit::kN), 25.0);
        assert_eq!(f3[1].to(ForceUnit::kN), 60.0);
    }

    #[test]
    fn test_force_subtraction_arr2() {
        let f1 = arr2(&[[
            Force::new(50.0, ForceUnit::kN),
            Force::new(75.0, ForceUnit::kN),
        ]]);
        let f2 = arr2(&[[
            Force::new(25.0, ForceUnit::kN),
            Force::new(15.0, ForceUnit::kN),
        ]]);
        let f3 = f1 - f2;
        assert_eq!(f3[[0, 0]].to(ForceUnit::kN), 25.0);
        assert_eq!(f3[[0, 1]].to(ForceUnit::kN), 60.0);
    }

    #[test]
    fn test_force_multiplication() {
        let f = Force::new(10.0, ForceUnit::kN);
        let f2 = f * 2.5;
        assert_eq!(f2.to(ForceUnit::kN), 25.0);
    }

    #[test]
    fn test_force_multiplication_arr1() {
        let f1 = arr1(&[Force::new(10.0, ForceUnit::kN)]);
        let f2 = f1 * 2.5;
        assert_eq!(f2[0].to(ForceUnit::kN), 25.0);
    }

    #[test]
    fn test_force_multiplication_arr2() {
        let f1 = arr2(&[[Force::new(10.0, ForceUnit::kN)]]);
        let f2 = f1 * 2.5;
        assert_eq!(f2[[0, 0]].to(ForceUnit::kN), 25.0);
    }

    #[test]
    fn test_force_division() {
        let f = Force::new(25.0, ForceUnit::kN);
        let f2 = f / 5.0;
        assert_eq!(f2.to(ForceUnit::kN), 5.0);
    }

    #[test]
    fn test_force_division_arr1() {
        let f1 = arr1(&[Force::new(25.0, ForceUnit::kN)]);
        let f2 = f1 / 5.;
        assert_eq!(f2[0].to(ForceUnit::kN), 5.0);
    }

    #[test]
    fn test_force_division_arr2() {
        let f1 = arr2(&[[Force::new(25.0, ForceUnit::kN)]]);
        let f2 = f1 / 5.;
        assert_eq!(f2[[0, 0]].to(ForceUnit::kN), 5.);
    }

    #[test]
    fn test_force_display() {
        let f = Force::new(10.0, ForceUnit::N);
        assert_eq!(f.to_string(), "10 N");
    }

    #[test]
    fn test_force_rounding() {
        let f = Force::new(9.9999, ForceUnit::N);
        assert_eq!(f.to_string(), "10 N");
    }

    #[test]
    fn test_force_rounding_zero() {
        let f = Force::zero();
        assert_eq!(f.to_string(), "0 N");
    }

    #[test]
    fn test_force_rounding_override() {
        let f = Force::new(100000., ForceUnit::N);
        assert_eq!(f.to_string(), "100000 N");
    }

    #[test]
    fn test_inf() {
        let f = Force::new(f64::INFINITY, ForceUnit::N);
        assert!(f.get_multiplier().is_infinite());
        assert!(!f.get_multiplier().is_sign_negative());
        assert!(f.as_f64().is_infinite());
        assert!(!f.as_f64().is_sign_negative());
    }

    #[test]
    fn test_neg_inf() {
        let f = Force::new(f64::NEG_INFINITY, ForceUnit::N);
        assert!(f.get_multiplier().is_infinite());
        assert!(f.get_multiplier().is_sign_negative());
        assert!(f.as_f64().is_infinite());
        assert!(f.as_f64().is_sign_negative());
    }
}

#[cfg(test)]
mod test_distance {
    use unitforge::prelude::*;
    use unitforge::quantities::*;
    use unitforge::AreaUnit;

    #[test]
    fn test_distance_creation() {
        let d = Distance::new(100.0, DistanceUnit::km);
        assert_eq!(d.to(DistanceUnit::m), 100_000.0);
    }

    #[test]
    fn test_distance_conversion() {
        let d = Distance::new(1.0, DistanceUnit::km);
        assert_eq!(d.to(DistanceUnit::m), 1_000.0);
        assert_eq!(d.to(DistanceUnit::dm), 10_000.0);
        assert_eq!(d.to(DistanceUnit::cm), 100_000.0);
        assert_eq!(d.to(DistanceUnit::mm), 1_000_000.0);
    }

    #[test]
    fn test_distance_addition() {
        let d1 = Distance::new(500.0, DistanceUnit::m);
        let d2 = Distance::new(1.0, DistanceUnit::km);
        let d3 = d1 + d2;
        assert_eq!(d3.to(DistanceUnit::m), 1_500.0);
    }

    #[test]
    fn test_distance_subtraction() {
        let d1 = Distance::new(2.0, DistanceUnit::km);
        let d2 = Distance::new(500.0, DistanceUnit::m);
        let d3 = d1 - d2;
        assert_eq!(d3.to(DistanceUnit::m), 1_500.0);
    }

    #[test]
    fn test_distance_multiplication() {
        let d = Distance::new(100.0, DistanceUnit::m);
        let d_multiplied = d * 2.5;
        let d_multiplied_swapped = 2.5 * d;
        assert_eq!(d_multiplied.to(DistanceUnit::m), 250.0);
        assert_eq!(d_multiplied_swapped.to(DistanceUnit::m), 250.0);
    }

    #[test]
    fn test_distance_division() {
        let d = Distance::new(500.0, DistanceUnit::m);
        let d_divided = d / 5.0;
        assert_eq!(d_divided.to(DistanceUnit::m), 100.0);
    }

    #[test]
    fn test_distance_division_by_division() {
        let d_1 = Distance::new(500.0, DistanceUnit::m);
        let d_2 = Distance::new(250.0, DistanceUnit::m);
        assert_eq!(d_1 / d_2, 2.0);
    }

    #[test]
    fn test_distance_display() {
        let d = Distance::new(100.0, DistanceUnit::m);
        assert_eq!(d.to_string(), "100000 mm");
    }

    #[test]
    fn test_distance_multiplication_with_self() {
        let d_1 = Distance::new(100.0, DistanceUnit::m);
        let d_2 = Distance::new(2.0, DistanceUnit::m);
        let a = d_1 * d_2;
        assert_eq!(a.to(AreaUnit::msq), 200.0);
    }

    #[test]
    fn test_equality() {
        let d_1 = Distance::new(100.0, DistanceUnit::m);
        let d_2 = Distance::new(2.0, DistanceUnit::m);

        assert!(d_1.is_close(&(d_2 * 50.0), &(d_2 / 100.0)));
    }
}

#[cfg(test)]
mod test_stiffness {
    use unitforge::prelude::*;
    use unitforge::quantities::{Stiffness, StiffnessUnit};

    #[test]
    fn test_stiffness_creation() {
        let s = Stiffness::new(1.0, StiffnessUnit::N_m);
        assert_eq!(s.to(StiffnessUnit::N_m), 1.0);
        assert_eq!(s.to(StiffnessUnit::kN_m), 0.001);
    }

    #[test]
    fn test_stiffness_conversion() {
        let s = Stiffness::new(1.0, StiffnessUnit::N_m);
        assert_eq!(s.to(StiffnessUnit::N_mm), 0.001);
        assert_eq!(s.to(StiffnessUnit::kN_mm), 0.000001);
    }

    #[test]
    fn test_stiffness_addition() {
        let s1 = Stiffness::new(1.0, StiffnessUnit::N_m);
        let s2 = Stiffness::new(1.0, StiffnessUnit::N_m);
        let s3 = s1 + s2;
        assert_eq!(s3.to(StiffnessUnit::N_m), 2.0);
    }

    #[test]
    fn test_stiffness_subtraction() {
        let s1 = Stiffness::new(3.0, StiffnessUnit::N_m);
        let s2 = Stiffness::new(1.0, StiffnessUnit::N_m);
        let s3 = s1 - s2;
        assert_eq!(s3.to(StiffnessUnit::N_m), 2.0);
    }

    #[test]
    fn test_stiffness_multiplication() {
        let s = Stiffness::new(1.0, StiffnessUnit::N_m);
        let s_multiplied = s * 2.5;
        assert_eq!(s_multiplied.to(StiffnessUnit::N_m), 2.5);
    }

    #[test]
    fn test_stiffness_division() {
        let s = Stiffness::new(5.0, StiffnessUnit::N_m);
        let s_divided = s / 5.0;
        assert_eq!(s_divided.to(StiffnessUnit::N_m), 1.0);
    }

    #[test]
    fn test_stiffness_display() {
        let s = Stiffness::new(1.0, StiffnessUnit::N_m);
        assert_eq!(s.to_string(), "0.001 N/mm");
    }
}

#[cfg(test)]
mod test_inverse_distance {
    use super::approx_eq;
    use unitforge::quantities::*;
    use unitforge::{InverseDistanceUnit, PhysicsQuantity};

    #[test]
    fn test_new() {
        let id = InverseDistance::new(10_f64, InverseDistanceUnit::_mm);
        assert!(approx_eq(id.to(InverseDistanceUnit::_cm), 100_f64, 10E-10));
    }

    #[test]
    fn test_mul_with_distance() {
        let d = Distance::new(0.1_f64, DistanceUnit::mm);
        let id = InverseDistance::new(10_f64, InverseDistanceUnit::_mm);
        assert!(approx_eq(d * id, 1_f64, 10E-10));
        assert!(approx_eq(id * d, 1_f64, 10E-10));
    }
}

#[cfg(test)]
mod test_angle {
    use num_traits::Zero;
    use std::f64::consts::PI;
    use unitforge::prelude::*;
    use unitforge::{Angle, AngleUnit};

    #[test]
    fn test_angle_creation_and_conversion() {
        let angle_rad = Angle::new(PI, AngleUnit::rad);
        assert!((angle_rad.to(AngleUnit::rad) - PI).abs() < 1e-10);
        assert!((angle_rad.to(AngleUnit::deg) - 180.0).abs() < 1e-10);

        let angle_deg = Angle::new(90.0, AngleUnit::deg);
        assert!((angle_deg.to(AngleUnit::rad) - (PI / 2.0)).abs() < 1e-10);
        assert!((angle_deg.to(AngleUnit::deg) - 90.0).abs() < 1e-10);
    }

    #[test]
    fn test_trigonometric_functions() {
        let angle = Angle::new(PI / 2.0, AngleUnit::rad);
        assert!((angle.sin() - 1.0).abs() < 1e-10);
        assert!(angle.cos().abs() < 1e-10);
        assert!((Angle::new(45., AngleUnit::deg).tan() - 1.).abs() < 1e-10);
    }

    #[test]
    fn test_arc_functions() {
        let sin_value = 0.5;
        let arc_sin = Angle::arc_sin(sin_value);
        assert!((arc_sin.to(AngleUnit::rad) - sin_value.asin()).abs() < 1e-10);

        let cos_value = 0.5;
        let arc_cos = Angle::arc_cos(cos_value);
        assert!((arc_cos.to(AngleUnit::rad) - cos_value.acos()).abs() < 1e-10);

        let tan_value = 1.0;
        let arc_tan = Angle::arc_tan(tan_value);
        assert!((arc_tan.to(AngleUnit::rad) - tan_value.atan()).abs() < 1e-10);
    }

    #[test]
    fn test_angle_display() {
        let angle = Angle::new(PI, AngleUnit::rad);
        assert_eq!(format!("{}", angle), "180°");
    }

    #[test]
    fn test_zero_angle() {
        let zero_angle = Angle::zero();
        assert!((zero_angle.to(AngleUnit::rad) - 0.0).abs() < 1e-10);
        assert!((zero_angle.to(AngleUnit::deg) - 0.0).abs() < 1e-10);
    }

    #[test]
    fn test_arctan2_45_deg() {
        let angle = Angle::arc_tan_2(1.0, 1.0);
        let expected_deg = 45.0;
        let diff = (angle.to(AngleUnit::deg) - expected_deg).abs();
        assert!(diff < 1e-10);
    }

    #[test]
    fn test_arctan2_90_deg() {
        let angle = Angle::arc_tan_2(1.0, 0.0);
        let expected_deg = 90.0;
        let diff = (angle.to(AngleUnit::deg) - expected_deg).abs();
        assert!(diff < 1e-10);
    }

    #[test]
    fn test_arctan2_minus_45_deg() {
        let angle = Angle::arc_tan_2(-1.0, 1.0);
        let expected_deg = -45.0;
        let diff = (angle.to(AngleUnit::deg) - expected_deg).abs();
        assert!(diff < 1e-10);
    }

    #[test]
    fn test_arctan2_180_deg() {
        let angle = Angle::arc_tan_2(0.0, -1.0);
        let expected_deg = 180.0;
        let actual_deg = angle.to(AngleUnit::deg);
        let wrapped = if actual_deg < -180.0 {
            actual_deg + 360.0
        } else if actual_deg > 180.0 {
            actual_deg - 360.0
        } else {
            actual_deg
        };
        let diff = (wrapped - expected_deg).abs();
        assert!(diff < 1e-10);
    }
}

#[cfg(test)]
mod test_constant {
    use unitforge::{PhysicsQuantity, Velocity, VelocityUnit};

    #[test]
    fn c() {
        let c = Velocity::c();
        assert_eq!(c.to(VelocityUnit::m_s), 299792458.0);
    }
}

#[cfg(test)]
mod test_connections {
    use super::approx_eq;
    use ndarray::{arr1, arr2};
    use unitforge::prelude::*;
    use unitforge::quantities::*;

    #[test]
    fn test_force_division_to_stiffness() {
        let f = Force::new(100.0, ForceUnit::N);
        let d = Distance::new(10.0, DistanceUnit::m);

        let s = f / d;

        assert!(approx_eq(s.to(StiffnessUnit::N_m), 10.0, 1E-10));
    }

    #[test]
    fn test_force_multiplication_to_moment_arr1() {
        let f = arr1(&[Force::new(100.0, ForceUnit::N)]);
        let d = arr1(&[Distance::new(5.0, DistanceUnit::m)]);

        let m_1 = f.clone().mul_array1(d.clone());
        let m_2 = d.clone().mul_array1(f.clone());
        assert!(approx_eq(m_1[0].to(ForceDistanceUnit::Nm), 500.0, 1E-10));
        assert!(approx_eq(m_2[0].to(ForceDistanceUnit::Nm), 500.0, 1E-10));
    }

    #[test]
    fn test_force_multiplication_to_moment_arr2() {
        let f = arr2(&[[Force::new(100.0, ForceUnit::N)]]);
        let d = arr2(&[[Distance::new(5.0, DistanceUnit::m)]]);

        let m_1 = d.clone().mul_array2(f.clone()).unwrap();
        let m_2 = f.clone().mul_array2(d.clone()).unwrap();
        assert!(approx_eq(
            m_1[[0, 0]].to(ForceDistanceUnit::Nm),
            500.0,
            1E-10
        ));
        assert!(approx_eq(
            m_2[[0, 0]].to(ForceDistanceUnit::Nm),
            500.0,
            1E-10
        ));
    }

    #[test]
    fn test_stiffness_multiplication_to_force() {
        let s = Stiffness::new(10.0, StiffnessUnit::N_m);
        let d = Distance::new(10.0, DistanceUnit::m);

        let f = s * d;

        assert!(approx_eq(f.to(ForceUnit::N), 100.0, 1E-10));
    }

    #[test]
    fn test_force_division_to_distance() {
        let f = Force::new(100.0, ForceUnit::N);
        let s = Stiffness::new(10.0, StiffnessUnit::N_m);

        let d = f / s;

        assert!(approx_eq(d.to(DistanceUnit::m), 10.0, 1E-10));
    }

    #[test]
    fn test_area_division_by_distance() {
        let a = Area::new(100.0, AreaUnit::msq);
        let d = Distance::new(500., DistanceUnit::cm);

        let d_2 = a / d;

        assert!(approx_eq(d_2.to(DistanceUnit::m), 20.0, 1E-10));
    }

    #[test]
    fn test_distance_times_distance() {
        let d = Distance::new(500., DistanceUnit::cm);
        let d_2 = Distance::new(20., DistanceUnit::m);
        let a = d * d_2;
        assert!(approx_eq(a.to(AreaUnit::msq), 100.0, 1E-10));
    }

    #[test]
    fn test_distance_multiplication_with_self_arr1() {
        let d_1 = arr1(&[Distance::new(100.0, DistanceUnit::m)]);
        let d_2 = arr1(&[Distance::new(2.0, DistanceUnit::m)]);
        let a = d_1.mul_array1(d_2);
        assert_eq!(a[0].to(AreaUnit::msq), 200.0);
    }

    #[test]
    fn test_distance_multiplication_with_self_arr2() {
        let d_1 = arr2(&[[Distance::new(100.0, DistanceUnit::m)]]);
        let d_2 = arr2(&[[Distance::new(2.0, DistanceUnit::m)]]);
        let a = d_1.mul_array2(d_2).unwrap();
        assert_eq!(a[[0, 0]].to(AreaUnit::msq), 200.0);
    }

    #[test]
    fn test_moment_division_by_distance() {
        let m = ForceDistance::new(100., ForceDistanceUnit::Ncm);
        let d = Distance::new(0.2, DistanceUnit::m);
        let f = m / d;
        assert!(approx_eq(f.to(ForceUnit::N), 5., 1E-10));
    }

    #[test]
    fn test_moment_division_by_distance_arr1() {
        let m = arr1(&[ForceDistance::new(100., ForceDistanceUnit::Ncm)]);
        let d = arr1(&[Distance::new(0.2, DistanceUnit::m)]);
        let f = m.div_array1(d);
        assert!(approx_eq(f[0].to(ForceUnit::N), 5., 1E-10));
    }

    #[test]
    fn test_moment_division_by_distance_arr2() {
        let m = arr2(&[[ForceDistance::new(100., ForceDistanceUnit::Ncm)]]);
        let d = arr2(&[[Distance::new(0.2, DistanceUnit::m)]]);
        let f = m.div_array2(d).unwrap();
        assert!(approx_eq(f[[0, 0]].to(ForceUnit::N), 5., 1E-10));
    }

    #[test]
    fn test_moment_division_by_force() {
        let m = ForceDistance::new(100., ForceDistanceUnit::Ncm);
        let f = Force::new(5.0, ForceUnit::N);
        let d = m / f;
        assert!(approx_eq(d.to(DistanceUnit::m), 0.2, 1E-10));
    }

    #[test]
    fn test_multiply_distance_with_force() {
        let f = Force::new(5.0, ForceUnit::N);
        let d = Distance::new(0.2, DistanceUnit::m);
        let m_sol = ForceDistance::new(100., ForceDistanceUnit::Ncm);
        assert!(approx_eq((d * f).as_f64(), m_sol.as_f64(), 1E-10));
        assert!(approx_eq((f * d).as_f64(), m_sol.as_f64(), 1E-10));
    }

    #[test]
    fn test_multiply_stress_with_area() {
        let a = Area::new(100., AreaUnit::mmsq);
        let s = Stress::new(50., StressUnit::MPa);
        assert!(approx_eq((s * a).to(ForceUnit::kN), 5., 1E-10));
        assert!(approx_eq((a * s).to(ForceUnit::kN), 5., 1E-10));
    }

    #[test]
    fn test_multiply_stress_with_force() {
        let f = Force::new(5., ForceUnit::kN);
        let s = Stress::new(50., StressUnit::MPa);
        assert!(approx_eq((f / s).to(AreaUnit::mmsq), 100., 1E-10));
    }

    #[test]
    fn test_divide_force_by_area() {
        let f = Force::new(5., ForceUnit::kN);
        let a = Area::new(100., AreaUnit::mmsq);
        assert!(approx_eq((f / a).to(StressUnit::MPa), 50., 1E-10));
    }

    #[test]
    fn test_divide_volume_by_area() {
        let v = Volume::new(100., VolumeUnit::mcb);
        let a = Area::new(10., AreaUnit::msq);
        assert!(approx_eq((v / a).to(DistanceUnit::m), 10., 1E-10));
    }

    #[test]
    fn test_divide_volume_by_distance() {
        let v = Volume::new(100., VolumeUnit::mcb);
        let d = Distance::new(10., DistanceUnit::m);
        assert!(approx_eq((v / d).to(AreaUnit::msq), 10., 1E-10));
    }

    #[test]
    fn test_multiply_distance_with_volume() {
        let a = Area::new(10., AreaUnit::msq);
        let d = Distance::new(10., DistanceUnit::m);
        assert!(approx_eq((d * a).to(VolumeUnit::mcb), 100., 1E-10));
        assert!(approx_eq((a * d).to(VolumeUnit::mcb), 100., 1E-10));
    }

    #[test]
    fn test_divide_mass_by_volume() {
        let v = Volume::new(10., VolumeUnit::mcb);
        let m = Mass::new(0.02, MassUnit::t);
        assert!(approx_eq((m / v).to(DensityUnit::kg_mcb), 2., 1E-10));
    }

    #[test]
    fn test_multiply_density_with_volume() {
        let rho = Density::new(2., DensityUnit::kg_mcb);
        let v = Volume::new(10., VolumeUnit::mcb);
        assert!(approx_eq((rho * v).to(MassUnit::kg), 20., 1E-10));
        assert!(approx_eq((v * rho).to(MassUnit::kg), 20., 1E-10));
    }

    #[test]
    fn test_divide_mass_by_density() {
        let rho = Density::new(2., DensityUnit::kg_mcb);
        let m = Mass::new(20., MassUnit::kg);
        assert!(approx_eq((m / rho).to(VolumeUnit::mcb), 10., 1E-10));
    }

    #[test]
    fn test_mul_inverse_distance_by_stress() {
        let id = InverseDistance::new(100_f64, InverseDistanceUnit::_mm);
        let s = Stress::new(10_f64, StressUnit::MPa);
        assert!(approx_eq(
            (s * id).to(ForcePerVolumeUnit::N_mmcb),
            1000.,
            1E-10
        ));
    }

    #[test]
    fn test_mul_inverse_distance_by_moment() {
        let id = InverseDistance::new(100_f64, InverseDistanceUnit::_mm);
        let m = ForceDistance::new(10_f64, ForceDistanceUnit::Nmm);
        assert!(approx_eq((m * id).to(ForceUnit::N), 1000., 1E-10));
    }

    #[test]
    fn test_comparison() {
        let a = Area::new(100., AreaUnit::mmsq);
        let b = Area::new(100., AreaUnit::mmsq);
        let c = Area::new(200., AreaUnit::mmsq);
        assert_eq!(a, b);
        assert_ne!(a, c);
        assert!(a < c);
        assert!(c > a);
        assert!(a <= b);
        assert!(a >= b);
        assert!(a <= c);
        assert!(c >= a);
    }
}

#[cfg(test)]
mod test_quantity_enum {
    use crate::approx_eq;
    use unitforge::{
        Distance, DistanceUnit, Force, ForceDistanceUnit, ForceUnit, Mass, MassUnit,
        PhysicsQuantity, Quantity, StiffnessUnit, Unit,
    };

    #[test]
    fn test_add() {
        let a = Quantity::MassQuantity(Mass::new(12., MassUnit::kg));
        let b = Quantity::MassQuantity(Mass::new(10., MassUnit::kg));
        let c = (a + b).unwrap();
        assert!(approx_eq(
            c.to(Unit::MassUnit(MassUnit::kg)).unwrap(),
            22.,
            1E-10
        ));
    }

    #[test]
    fn test_add_fail() {
        let a = Quantity::MassQuantity(Mass::new(12., MassUnit::kg));
        let b = Quantity::FloatQuantity(3.);
        assert!((a + b).is_err());
    }

    #[test]
    fn test_sub() {
        let a = Quantity::MassQuantity(Mass::new(12., MassUnit::kg));
        let b = Quantity::MassQuantity(Mass::new(10., MassUnit::kg));
        let c = (a - b).unwrap();
        assert!(approx_eq(
            c.to(Unit::MassUnit(MassUnit::kg)).unwrap(),
            2.,
            1E-10
        ));
    }

    #[test]
    fn test_sub_fail() {
        let a = Quantity::MassQuantity(Mass::new(12., MassUnit::kg));
        let b = Quantity::FloatQuantity(3.);
        assert!((a - b).is_err());
    }

    #[test]
    fn test_mul() {
        let a = Quantity::ForceQuantity(Force::new(3., ForceUnit::N));
        let b = Quantity::DistanceQuantity(Distance::new(4., DistanceUnit::m));
        let c = (a * b).unwrap();
        assert!(approx_eq(
            c.to(Unit::ForceDistanceUnit(ForceDistanceUnit::Nm))
                .unwrap(),
            12.,
            1E-10
        ));
    }

    #[test]
    fn test_div() {
        let a = Quantity::ForceQuantity(Force::new(3., ForceUnit::N));
        let b = Quantity::DistanceQuantity(Distance::new(4., DistanceUnit::m));
        let c = (a / b).unwrap();
        assert!(approx_eq(
            c.to(Unit::StiffnessUnit(StiffnessUnit::N_m)).unwrap(),
            3. / 4.,
            1E-10
        ));
    }

    #[test]
    fn test_abs() {
        let a = Quantity::DistanceQuantity(Distance::new(-4., DistanceUnit::m));
        assert!(approx_eq(
            a.abs().to(Unit::DistanceUnit(DistanceUnit::m)).unwrap(),
            4.,
            1E-10
        ));
    }

    #[test]
    fn test_unit_name() {
        let u = Unit::DistanceUnit(DistanceUnit::m);
        assert_eq!(u.get_name(), "m");
    }

    #[test]
    fn test_is_not_nan() {
        let f = Quantity::DistanceQuantity(Distance::new(-4., DistanceUnit::m));
        assert!(!f.is_nan());
    }

    #[test]
    fn test_is_nan() {
        let f = Quantity::DistanceQuantity(Distance::new(f64::NAN, DistanceUnit::m));
        assert!(f.is_nan());
    }
}
