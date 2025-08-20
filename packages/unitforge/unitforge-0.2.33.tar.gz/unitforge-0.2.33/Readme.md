# Unitforge

## Overview

**Unitforge** is a Rust crate designed for safe handling of physical quantities of units. New quantities and relations can be set up via small macros.

## Features

- **Quantity inference:** Resulting quantities of arithmetic operations are inferred at compile time.
- **Unit conversion:** Quantities can be set or read in arbitrary units.
- **Computing Precision** Values are stored in exponential format (f64*10^i32) to prevent floating point precision issues.
- **Formating** Quantities are displayed with 4 significant digits and configured display unit.
- **ndarray support:** Quantities may be used as inner types for `ndarray`.
- **3D Vector and matrix operations:** Structs for 3D vectors and matrices are included to allow fast and unit-safe work with them.
- **Serialization**: Optional support for sere using the serde feature.
- **python interface** Optional Python interface when building with flag pyo3; also available on pypi

## Contribute

All contributions are welcome! Feel free to implement new quantities or define relations using `impl_macros.rs`. 🚀
