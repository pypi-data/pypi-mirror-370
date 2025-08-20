#![cfg(all(test, feature = "serde"))]

use crate::{
    quantities::*,
    small_linalg::{Matrix3, Vector3},
    PhysicsQuantity,
};
use ndarray::arr1;

#[test]
fn roundtrip_quantity() {
    let original = Force::new(100.0, ForceUnit::kN);

    let json = serde_json::to_string(&original).expect("Failed to serialize ");

    let deserialized: Force = serde_json::from_str(&json).expect("Failed to deserialize ");

    assert_eq!(deserialized.to(ForceUnit::N), original.to(ForceUnit::N));
}

#[test]
fn roundtrip_quantity_ndarray() {
    let original = arr1(&[
        Force::new(50.0, ForceUnit::kN),
        Force::new(75.0, ForceUnit::kN),
    ]);
    let json = serde_json::to_string(&original).expect("Failed to serialize ");

    let deserialized: ndarray::ArrayBase<ndarray::OwnedRepr<Force>, ndarray::Dim<[usize; 1]>> =
        serde_json::from_str(&json).expect("Failed to deserialize ");

    assert_eq!(
        deserialized[1].to(ForceUnit::N),
        original[1].to(ForceUnit::N)
    );
}
#[test]
fn roundtrip_vector() {
    let original: Vector3<Force> = Vector3::from_f64([1.0, 2.0, 3.0]);

    let json = serde_json::to_string(&original).expect("Failed to serialize ");

    let deserialized: Vector3<Force> = serde_json::from_str(&json).expect("Failed to deserialize ");

    assert_eq!(deserialized, original);
}

#[test]
fn roundtrip_matrix() {
    let mat = Matrix3::new([[3_f64; 3]; 3]);
    let f = Force::new(1., ForceUnit::kN);
    let original = mat * f;

    let json = serde_json::to_string(&original).expect("Failed to serialize ");

    let deserialized: Matrix3<Force> = serde_json::from_str(&json).expect("Failed to deserialize ");

    for i in 0..3 {
        for j in 0..3 {
            assert_eq!(deserialized[(i, j)], Force::new(3., ForceUnit::kN))
        }
    }
}
