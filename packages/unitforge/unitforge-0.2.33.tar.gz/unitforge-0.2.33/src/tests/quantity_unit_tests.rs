#![cfg(test)]
mod tests {
    use crate::*;
    use num_traits::Zero;

    #[test]
    fn test_new() {
        let input = 1000;
        let output = Distance::new(input.into(), DistanceUnit::mm);
        assert_eq!(
            output,
            Distance {
                multiplier: 1000f64,
                power: -3
            }
        )
    }

    #[test]
    fn optimize_on_add() {
        let f_1 = Force::new(10.0, ForceUnit::N);
        let f_2 = Force::new(1.0E12, ForceUnit::N);
        let f = f_1 + f_2;
        assert!(f.get_multiplier().log10().round() == 0.);
    }

    #[test]
    fn optimize_large() {
        let mut x = Force {
            multiplier: 1E10,
            power: 0,
        };
        x.optimize();
        assert!(x.get_multiplier().log10().round() == 0.);
        assert_eq!(x.to(ForceUnit::N), 1E10);
    }

    #[test]
    fn optimize_small() {
        let mut x = Force {
            multiplier: 1E-10,
            power: 0,
        };
        x.optimize();
        assert!(x.get_multiplier().log10().round() == 0.);
        assert_eq!(x.to(ForceUnit::N), 1E-10);
    }

    #[test]
    fn optimize_zero() {
        let mut f_1 = Force::zero();
        f_1.optimize();
        assert_eq!(f_1, Force::zero());
    }

    #[test]
    fn mul_with_self() {
        let a = Quantity::AreaQuantity(Area::new(10.0, AreaUnit::msq));
        let b = (a * a).unwrap();
        assert_eq!(
            b.to(Unit::AreaOfMomentUnit(AreaOfMomentUnit::mhc)).unwrap(),
            100.0
        );
    }

    #[test]
    fn sqrt() {
        let a = Quantity::AreaOfMomentQuantity(AreaOfMoment::new(25.0, AreaOfMomentUnit::mhc));
        let b = a.sqrt().unwrap();
        assert!((b.to(Unit::AreaUnit(AreaUnit::msq)).unwrap() - 5.0).abs() < 1E-10);
    }
}
